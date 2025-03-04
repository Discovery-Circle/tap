import warnings
import itertools
from scipy import stats
import plotly.express as px
import scikit_posthocs as sp
from statsmodels.stats.multitest import multipletests
warnings.simplefilter(action='ignore', category=FutureWarning)

def plot_stats(
        df,
        x,
        y,
        pairs = None,
        order = None,
        type_plot="box",
        type_test="mann-whitney",
        type_correction = None,
        subcategory = None,
        cutoff_pvalue = 0.05,
        filename = None,
        export_size = (800, 600, 3),
        kwargs = {}
    ):
    '''
        It's a function to make statistical tests and add statistical annotations on Plotly graph

        Parameters
        --------
        df : DataFrame
        x : str
        y : str
        pairs : list of str tuple (default is None)
        order : list (default is None)
        type_plot: str (dafult is box)
        type_test : str (default is Mann-Whitney)
        type_correction : str (default is None)
        subcategory : str (default is None)
        cutoff_pvalue : float (default is 0.05)
        filename: str (default is None)
        export_size: int tuple (default is (800, 600, 3))
        kwargs : dict (dafult is empty)

        Returns
        --------
        None
    '''
    #SET TYPE TEST AND TEST CORRECTION TO LOWERCASE
    type_test=type_test.lower()
    if type_correction is not None:
        type_correction=type_correction.lower()

    #ALL X INSIDE DATAFRAME
    all_x = list(df[x].unique())
    y_plot = y

    #ORDER ELEMENTS
    if order is None:
        order = all_x
    else:
        #CONTROL order PARAM
        for _element in order:
            if _element not in all_x:
                raise NameError(f"Element '{_element}' not found inside dataframe: {all_x}")
        if len(set(order)) != len(all_x):
                raise NameError(f"Expected all entries, {list(set(all_x).difference(order))} not found")
        all_x = order
  
    #SCALE Y LOG10
    if kwargs.get("log_y", False):
      from math import log10
      del kwargs["log_y"]
      def funzione_scaling(param_x):
        if param_x >0:
          return log10(param_x)
        elif param_x==0:
          return 0
        else:
          return -(log10(abs(param_x)))

      new_column_name = f"log10({y})"
      df[new_column_name] = df[y].apply(lambda x: funzione_scaling(x))
      y_plot = new_column_name

    #CALCULATE VERTICAL MIN, MAX AND SINGLE UNIT
    v_min = min(df[y_plot].values)
    v_max = max(df[y_plot].values)
    v_unit = (v_max - v_min) * 0.1

    #FIND ALL GROUP
    if subcategory is None or subcategory == x:
        subcategory = None
        all_groups = all_x
    else:
        all_sub_category = list(df[subcategory].unique())
        all_groups = []
        for _single_x in all_x:
            _subs = df[df[x]==_single_x][subcategory].unique()
            _subs_sorted = sorted(_subs)
            for _sub in _subs_sorted:
                all_groups.append((_single_x, _sub))
    
    #CREATE PAIRS IF pairs IS NONE
    if pairs is None:
        if subcategory is None:
            pairs = list(itertools.combinations(all_groups, 2))
        else:
            pairs = []
            for _single_x in all_x:
                pairs += (list(itertools.combinations([_x for _x in all_groups if _x[0] == _single_x], 2)))

    #CALCULATED INFOS
    info_data = dict()
    for _index, _single_group in enumerate(all_groups):
        if subcategory is None:
            _values = df[df[x] == _single_group][y_plot].values
            if len(_values) > 0:
                info_data[_single_group] = {
                    "max": max(_values),
                    "index_class": _index,
                    "index_subclass": _index
                }
        else:
            _values = df[ (df[x] == _single_group[0]) & (df[subcategory] == _single_group[1]) ][y_plot].values
            if len(_values) > 0:
                info_data[_single_group] = {
                    "max": max(_values),
                    "index_class": all_x.index(_single_group[0]),
                    "index_subclass": _index
                }  

    #PLOT BASE
    fig=None
    match type_plot:
        case "box": 
            fig = px.box(df, x=x, y=y_plot, color=(x if subcategory is None else subcategory), category_orders={f"{x}": order}, **kwargs)
        case "strip":
            fig = px.strip(df, x=x, y=y_plot, color=(x if subcategory is None else subcategory), category_orders={f"{x}": order}, **kwargs)

    dunn_values = {}
    #In case of Dunn generate Map
    if type_test == "dunn":
        if subcategory is None:
            dunn_values = sp.posthoc_dunn(df, y, x).to_dict()
        else:
            for _val in all_x:
                dunn_values[_val] = sp.posthoc_dunn(df[df[x] == _val], y, subcategory).to_dict()

    p_values_obj = []
    #i == DISTANCE
    for i in range(1, len(all_groups)):
        _distance_dict = dict()
        #CALCULATE DISTANCES
        for _pair in pairs:
            if abs(info_data[_pair[0]]["index_subclass"] - info_data[_pair[1]]["index_subclass"]) == i:
                _distance_dict[_pair]=abs(info_data[_pair[0]]["max"] - info_data[_pair[1]]["max"])

        #SORT DISTANCES
        _distance_dict = dict(sorted(_distance_dict.items(), key=lambda x: x[1]))
        
        #GENERATE ANNOTATIONS
        for _pair in _distance_dict.keys():
            #GET VARS
            if subcategory is None:
                _values_p0 = df[df[x]==_pair[0]][y].values
                _values_p1 = df[df[x]==_pair[1]][y].values
            else:
                _values_p0 = df[ (df[x]==_pair[0][0]) & (df[subcategory]==_pair[0][1]) ][y].values
                _values_p1 = df[ (df[x]==_pair[1][0]) & (df[subcategory]==_pair[1][1]) ][y].values

            _index_class0 = info_data[_pair[0]]["index_class"]
            _index_class1 = info_data[_pair[1]]["index_class"]
            _index_subclass0 = info_data[_pair[0]]["index_subclass"]
            _index_subclass1 = info_data[_pair[1]]["index_subclass"]

            if _index_subclass0 < _index_subclass1:
                _slice_all_groups = all_groups[_index_subclass0:_index_subclass1 + 1]
            else:
                _slice_all_groups = all_groups[_index_subclass1:_index_subclass0 + 1]

            #GET MAX Y
            _value_line_y = 0
            for _key, _element in info_data.items():
                if _key in _slice_all_groups and _element["max"] > _value_line_y:
                    _value_line_y = _element["max"]
            #UPDATE MAX Y
            for _k in info_data.keys():
                if _k in _slice_all_groups:
                    info_data[_k]["max"] = _value_line_y + v_unit * 1.5
            _value_line_y += v_unit

            #PLOT LINE
            if subcategory is None:
                fig.add_shape(type="path",
                    path=f"M {_index_class0},{_value_line_y - (v_unit * 0.5)} L{_index_class0},{_value_line_y} L{_index_class1},{_value_line_y} L{_index_class1},{_value_line_y - (v_unit * 0.5)}", 
                    line=dict(color="Black",width=1.5)
                )
            else:
                #CALCULATE OFFSET FOR SUBCATEGORY
                _offset_default = (len(all_x) * 0.70) / (len(all_x) * len(all_sub_category))
                _half_dist = len(all_sub_category) // 2
                _dist0 = all_sub_category.index(_pair[0][1])
                _dist1 = all_sub_category.index(_pair[1][1])
                _offset0 = (_dist0 - _half_dist) * _offset_default
                _offset1 = (_dist1 - _half_dist) * _offset_default
                if len(all_sub_category) % 2 == 0:
                    _offset0 += _offset_default * 0.5
                    _offset1 += _offset_default * 0.5
                _index_class0 += _offset0
                _index_class1 += _offset1
                
                fig.add_shape(type="path",
                    path=f"M {_index_class0},{_value_line_y - (v_unit * 0.5)} L{_index_class0},{_value_line_y} L{_index_class1},{_value_line_y} L{_index_class1},{_value_line_y - (v_unit * 0.5)}", 
                    line=dict(color="Black",width=1.5)
                )

            #CALCULATE P_VALUE
            _pvalue = 0
            _statistic = 0
            match type_test:
                case "mann-whitney":
                    _statistic, _pvalue = stats.mannwhitneyu(_values_p0,_values_p1)
                case "t-test":
                    _statistic, _pvalue = stats.ttest_ind(_values_p0,_values_p1)
                case "t-test-related":
                    _statistic, _pvalue = stats.ttest_rel(_values_p0,_values_p1)
                case "wilcoxon":
                    _statistic, _pvalue = stats.wilcoxon(_values_p0,_values_p1)
                case "kruskal-wallis":
                    _statistic, _pvalue = stats.kruskal(_values_p0,_values_p1)
                case "levene":
                    _statistic, _pvalue = stats.levene(_values_p0,_values_p1)
                case "brunner-munzel":
                    _statistic, _pvalue = stats.brunnermunzel(_values_p0,_values_p1)
                case "ansari-bradley":
                    _statistic, _pvalue = stats.ansari(_values_p0,_values_p1)
                case "cramerVon-mises":
                    _res = stats.cramervonmises_2samp(_values_p0,_values_p1)
                    _statistic = _res.statistic
                    _pvalue = _res.pvalue
                case "kolmogorov-smirnov":
                    _statistic, _pvalue = stats.kstest(_values_p0,_values_p1)
                case "alexander-govern":
                    _res = stats.alexandergovern(_values_p0,_values_p1)
                    _statistic = _res.statistic
                    _pvalue = _res.pvalue
                case "fligner-killeen":
                    _statistic, _pvalue = stats.fligner(_values_p0,_values_p1)
                case "bartlett":
                    _statistic, _pvalue = stats.bartlett(_values_p0,_values_p1)
                case "dunn":
                    if subcategory is None:
                        _pvalue = dunn_values[_pair[0]][_pair[1]]
                    else:
                        _pvalue = dunn_values[_pair[0][0]][_pair[0][1]][_pair[1][1]]
                    _statistic = 0
                case _:
                    raise Exception(f"Type test {type_test} does not exist, use one of [mann-whitney,t-test,t-test-related,wilcoxon,kruskal-wallis,levene,brunner-munzel,ansari-bradley,cramervon-mises,kolmogorov-smirnov,alexander-govern,fligner-killeen,dunn]")

            p_values_obj.append(
                {
                    "x": (_index_class0 + _index_class1) * 0.5,
                    "y": _value_line_y + (v_unit * 0.5),
                    "p_value": _pvalue,
                    "stat": _statistic
                }
            )

    if type_correction is not None:
        _list_p_values = [_ele["p_value"] for _ele in p_values_obj]
        
        #https://www.statsmodels.org/dev/generated/statsmodels.stats.multitest.multipletests.html#statsmodels.stats.multitest.multipletests-parameters
        match type_correction:
            case "bonferroni":
                _result = multipletests(_list_p_values, method='bonferroni')
            case "sidak":
                _result = multipletests(_list_p_values, method='sidak')
            case "holm-sidak":
                _result = multipletests(_list_p_values, method='holm-sidak')
            case "benjamini-hochberg":
                _result = multipletests(_list_p_values, method='fdr_bh')
            case _:
                raise Exception(f"Type correction {type_correction} does not exist, use one of [bonferroni,sidak,holm-sidak,benjamini-hochberg]")

        for _index, _element in enumerate(p_values_obj):
            _element["p_value"] = _result[1][_index]

    for _element in p_values_obj:
        _color = "Green" if _element["p_value"] <= cutoff_pvalue else "Black"
        _pvalue = round(_element["p_value"], 3) if _element["p_value"] >= 0.001 else "< 0.001"
        #PLOT TEXT
        fig.add_annotation(
            x=_element["x"], y=_element["y"],
            text=f'p-value {_pvalue}',
            showarrow=False,
            font=dict(color=_color),
            hovertext=f'p-value: {_element["p_value"]}<br>statistic: {_element["stat"]}'
        )

    #UPDATE FIGURE RANGE Y
    fig['layout']['yaxis'].update(autorange = True)

    #PLOT OR SAVE FIGURE
    if filename is not None:
        if filename.endswith(".html"):
            fig.write_html(filename)
        else:
            fig.write_image(filename, format=filename.split(".")[-1], engine='kaleido', width=export_size[0], height=export_size[1], scale=export_size[2])
    
    return fig
