<p align="center">
  <img src="images/TAP.png" height=170>
</p>
<p align="center">
  <img src="images/TAP_text.png" height=100>
</p>

## 🚩 Index of Contents
- [What is TAP?](#-what-is-tap)
- [Features](#-features)
- [Installation](#-installation)
- [Examples](#-example)
- [Similar work](#-similar-work)
- [Contributors](#-contributors)

## 📌 What is TAP?

Python package to make statistical tests and add statistical annotations on plot generated with Plotly

## ✅ Features

- Single function to make statistical tests and add statistical annotations on plot generated with Plotly:
    - **Box plots**
    - **Strip plots**

- Integrated statistical tests (`scipy.stats` methods):
    - **Mann-Whitney test**
    - **t-test (independent and paired)**
    - **t-test-related (dipendent)**
    - **Levene test**
    - **Wilcoxon test**
    - **Kruskal-Wallis test**
    - **Brunner-Munzel test**
    - **Ansari-Bradley test**
    - **CramerVon-Mises test**
    - **Kolmogorov-Smirnov test**
    - **Alexander-Govern test**
    - **Fligner-Killeen test**
    - **Bartlett test**

- Correction for statistical tests can be applied (`statsmodel.stats.multitest.multipletests` method):
    - **Bonferroni**
    - **Sidak**
    - **Holm-Sidak**
    - **Benjamini-Hochberg**

## 📦 Installation
**TAP** is present on pipy, and can be downloaded directly with pip
```bash
pip install taplib
```
Or if you prefer you can clone the repository and install it manually
```bash
git clone https://github.com/FedericaPersiani/tap.git
cd tap
pip install .
```

## 🔍 Example
Once your dataframe has been loaded you can pass it to the "plot_stats" function which will apply the "Mann-Whitney" test by default on all classes present in the column indicated as **x**, using the **y** column as the value
```python
import tap
import seaborn as sns

df = sns.load_dataset("tips")
x = "day"
y = "total_bill"

tap.plot_stats(df, x, y)
```
![img](images/example_default.png)
---
**Cutoff pvalue**: You can change the significance of the null hypothesis through the **cutoff_pvalue** parameter, by default it is set to 0.05.
```python
tap.plot_stats(df, x, y, cutoff_pvalue=0.01)
```
![img](images/example_cutoff.png)
---
**Type test**: You can change the test type using the **type_test** parameter
```python
tap.plot_stats(df, x, y, type_test="CramerVon-Mises")
```
![img](images/example_test.png)
---
**Type correction**: You can apply a p-value correction algorithm via the **type_correction** parameter
```python
tap.plot_stats(df, x, y, type_correction="Bonferroni")
```
![img](images/example_correction.png)
---
**Order**: You can change the sorting of the plot by passing the list with all the entries present in the **x** column ordered as you prefer
```python
tap.plot_stats(df, x, y, order=["Thur", "Fri", "Sat", "Sun"])
```
![img](images/example_order.png)
---
**Type plot**: You can change the plot type using the **type_plot** parameter
```python
tap.plot_stats(df, x, y, type_plot="strip")
```
![img](images/example_plot.png)
---
**Pairs**: You can decide the pairs that will be used to generate the statistics to plot
```python
tap.plot_stats(df, x, y, pairs=[("Sun", "Sat"), ("Sun", "Thur")])
```
![img](images/example_pairs.png)
---
**Sub category**: Through the "sub_category" parameter it is possible to divide the various entries into a further sub-category, you can decide the various pairings using the **pairs** parameter but in this case you will need to declare them as a tuple (primary category, sub-category)
```python
tap.plot_stats(df, x, y, sub_category="sex")
```
![img](images/example_subcategory1.png)
```python
tap.plot_stats(df, x, y, sub_category="sex", pairs=[(("Sun", "Male"), ("Sat", "Male")), (("Sun", "Male"), ("Sun", "Female"))])
```
![img](images/example_subcategory2.png)
---
**Kwargs**: Through the **kwargs** parameter you can pass a key/value pairs directly to the plotly function, such as the size of the figure
```python
tap.plot_stats(df, x, y, kwargs={"width":500, "height":500})
```
![img](images/example_kwargs.png)

## 📝 Similar work
This repository is inspired by trevismd/statannotations ([Statannotations](https://github.com/trevismd/statannotations)), which compute statistical tests and annotations with seaborn

## ✨ Contributors
<table align="center">
  <tbody>
    <tr>
      <!-- FEDERICA PERSIANI -->
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/FedericaPersiani">
          <img src="https://avatars.githubusercontent.com/u/101985116?v=3?s=100" width="100px;" alt="Federica Persiani"/>
          <br />
          <sub>
            <b>Federica Persiani</b>
          </sub>
        </a>
        <br />
        <a title="Code">💻</a>
        <a title="Research">🔬</a>
      </td>
      <!-- DAMIANO MALORI -->
      <td align="center" valign="top" width="14.28%">
        <a href="https://github.com/demian2435">
          <img src="https://avatars.githubusercontent.com/u/28110775?v=3?s=100" width="100px;" alt="Damiano Malori"/>
          <br />
          <sub>
            <b>Damiano Malori</b>
          </sub>
        </a>
        <br />
        <a title="Code">💻</a>
        <a title="Packaging">📦</a>
      </td>
      <!-- END -->
    </tr>
  </tbody>
</table>