from scipy import stats
from statsmodels.stats.multitest import multipletests
import plotly.express as px
import itertools

def plot_stats(
        df,
        x,
        y,
        pairs = None,
        order = None,
        type_plot="box",
        type_test="Mann-Whitney",
        type_correction = None,
        kwargs = {}
    ):
    '''
        DOC
        ---
    '''
    #GET ALL CLASS
    all_x = list(df[x].unique())

    #CALCULATE MIN, MAX AND UNIT
    v_min = min(df[y].values)
    v_max = max(df[y].values)
    v_unit = (v_max - v_min) * 0.1

    #CREATE PAIRS IF pairs IS NONE
    if pairs is None:
        pairs = list(itertools.combinations(all_x, 2))

    if order is None:
        order = all_x
    else:
        for e in order:
            if e not in all_x:
                raise NameError(f"Element {e} not found inside dataframe")
        if len(set(order)) != len(all_x):
                raise NameError(f"Non tutti")
        all_x = order

    #CALCULATED INFOS
    info_data = dict()
    for index, single_x in enumerate(all_x):
        info_data[single_x] = {
            "max": max(df[df[x]==single_x][y].values),
            "index": index
        }

    #PLOT BASE
    fig=None
    match type_plot:
        case "box": 
            fig = px.box(df, x=x, y=y, color=x, category_orders={f"{x}": order}, **kwargs)
        case "strip":
            fig = px.strip(df, x=x, y=y, color=x, category_orders={f"{x}": order}, **kwargs)


    p_values_obj = []
    for i in range(1, len(all_x)):
        distance_dict = dict()
        #CALCULATE DISTANCES
        for pair in pairs:
            if abs(info_data[pair[0]]["index"] - info_data[pair[1]]["index"]) == i:
                distance_dict[pair]=abs(info_data[pair[0]]["max"] - info_data[pair[1]]["max"])

        #SORT DISTANCES
        distance_dict = dict(sorted(distance_dict.items(), key=lambda x: x[1]))

        #GENERATE ANNOTATIONS
        for pair in distance_dict.keys():
            #VARS PAIR 0
            values_p0 = df[df[x]==pair[0]][y].values
            index_class0 = info_data[pair[0]]["index"]
            #VARS PAIR 1
            values_p1 = df[df[x]==pair[1]][y].values
            index_class1 = info_data[pair[1]]["index"]

            if index_class0 < index_class1:
                slice_all_x = all_x[index_class0:index_class1 + 1]
            else:
                slice_all_x = all_x[index_class1:index_class0 + 1]

            value_line_y = 0
            column_selected = ""
            #GET MAX Y
            for k, e in info_data.items():
                if k in slice_all_x and e["max"] > value_line_y:
                    value_line_y = e["max"]
                    column_selected = k
            #UPDATE MAX Y
            for k, e in info_data.items():
                if k in slice_all_x:
                    info_data[k]["max"] = value_line_y + v_unit * 1.5
            value_line_y += v_unit

            #PLOT LINE
            fig.add_shape(type="path",
                path=f"M {index_class0},{value_line_y - (v_unit * 0.5)} L{index_class0},{value_line_y} L{index_class1},{value_line_y} L{index_class1},{value_line_y - (v_unit * 0.5)}", 
                line=dict(color="Black",width=1.5)
            )

            #CALCULATE P_VALUE
            p_value = 0
            match type_test:
                case "Mann-Whitney":
                    p_value = stats.mannwhitneyu(values_p0,values_p1)
                case "t-test":
                    p_value = stats.ttest_ind(values_p0,values_p1)
                case "t-test-related":
                    p_value = stats.ttest_rel(values_p0,values_p1)
                case "Wilcoxon":
                    p_value = stats.wilcoxon(values_p0,values_p1)
                case "Kruskal-Wallis":
                    p_value = stats.kruskal(values_p0,values_p1)
                case "Levene":
                    p_value = stats.levene(values_p0,values_p1)
                case "Brunner-Munzel":
                    p_value = stats.brunnermunzel(values_p0,values_p1)
                case "Ansari-Bradley":
                    p_value = stats.ansari(values_p0,values_p1)
                case "CramerVon-Mises":
                    p_value = stats.cramervonmises_2samp(values_p0,values_p1)
                case "Kolmogorov-Smirnov":
                    p_value = stats.kstest(values_p0,values_p1)
                case "Alexander-Govern":
                    p_value = stats.alexandergovern(values_p0,values_p1)
                case "Fligner-Killeen":
                    p_value = stats.fligner(values_p0,values_p1)
                case "Bartlett":
                    p_value = stats.bartlett(values_p0,values_p1)
                case _:
                    raise Exception(f"Type test {type_test} does not exist, use one of [Mann-Whitney,t-test,t-test-related,Wilcoxon,Kruskal-Wallis,Levene,Brunner-Munzel,Ansari-Bradley,CramerVon-Mises,Kolmogorov-Smirnov,Alexander-Govern,Fligner-Killeen]")

            p_values_obj.append(
                {
                    "x": (index_class0 + index_class1) * 0.5,
                    "y": value_line_y + (v_unit * 0.5),
                    "p_value": p_value.pvalue,
                    "stat": p_value.statistic
                }
            )

    if type_correction is not None:
        all_p_values = [e["p_value"] for e in p_values_obj]
        
        #https://www.statsmodels.org/dev/generated/statsmodels.stats.multitest.multipletests.html#statsmodels.stats.multitest.multipletests-parameters
        match type_correction:
            case "Bonferroni":
                result = multipletests(all_p_values, method='bonferroni')
            case "Sidak":
                result = multipletests(all_p_values, method='sidak')
            case "Holm-Sidak":
                result = multipletests(all_p_values, method='holm-sidak')
            case "Benjamini-Hochberg":
                result = multipletests(all_p_values, method='fdr_bh')
            case _:
                raise Exception(f"Type correction {type_correction} does not exist, use one of [Bonferroni,Sidak,Holm-Sidak,Benjamini-Hochberg]")

        for index, e in enumerate(p_values_obj):
            e["p_value"] = result[1][index]


    for ele in p_values_obj:
        color = "Green" if ele["p_value"] <= 0.05 else "Red"
        p_value = round(ele["p_value"], 3) if ele["p_value"] >= 0.001 else "< 0.001"
        #PLOT TEXT
        fig.add_annotation(
            x=ele["x"], y=ele["y"],
            text=f'p-value {p_value}',
            showarrow=False,
            font=dict(color=color),
            hovertext=f'p-value: {ele["p_value"]}<br>statistic: {ele["stat"]}'
        )

    #UPDATE FIGURE RANGE Y
    fig['layout']['yaxis'].update(autorange = True)

    #PLOT FIGURE
    fig.show()