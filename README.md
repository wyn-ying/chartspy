# echartspy

echarts库的 python 封装

考虑升级维护以及使用者学习负担，本库不对echarts的模型和属性进行python的对等映射

核心功能

* python配置转换成JavaScript的配置
  
* 渲染html文件，html字符串，jupyterlab输出，jupyter-notebook输出

辅助功能

* JavaScript配置 自动转换成 python配置
  
* pandas DataFrame可视化



## 使用说明

### 安装
```shell
pip install git+https://gitee.com/yiliuyan161/echartspy.git
```

### 升级 echartspy
```shell
pip uninstall echartspy -y  && pip install git+https://gitee.com/yiliuyan161/echartspy.git
```


### 升级echarts版本
```python
import echartspy
echartspy.ECHARTS_JS_URL = "https://unpkg.com/echarts@5.1.2/dist/echarts.min.js"
```

### 手写python配置绘图
```python
from echartspy import Echarts,Tools
options={
    'xAxis': {},
    'yAxis': {},
    'series': [{
        'symbolSize': 20,
        'data': [
            [10.0, 8.04],
            [8.07, 6.95],
            [13.0, 7.58],
            [9.05, 8.81],
            [11.0, 8.33]
        ],
        'type': 'scatter'
    }]
}
Echarts(options,height='600px',title='散点图测试').render_notebook()
```

### JavaScript配置自动转换
```python
from echartspy import Echarts,Tools
import echartspy.express as ex
js_str="""
{
    xAxis: {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    yAxis: {
        type: 'value'
    },
    series: [{
        data: [820, 932, 901, 934, 1290, 1330, 1320],
        type: 'line',
        smooth: true
    }]
}
"""
options=Tools.convert_js_to_dict(js_str,print_dict=False)
Echarts(options,height='600px').render_notebook()
```
![notebook环境输出](data:image/png;base64,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)



## 代码说明

### 包结构说明

#### echartspy包下使用两个对象 Echarts,Tools

Echarts对象接受 python配置，输出图表

Tools对象的静态方法有三个

* convert_js_to_dict JavaScript配置转换成python配置
* convert_to_list 辅助用户把DataFrame,Series,ndarray转换成list结构
* wrap_template 是一个模板工具函数，构建复杂图表可能会用到

#### echartspy.express包下是封装好的pandas DataFrame绘图函数

包含 bar,scatter,line,pie,candlestick,sankey,parallel,theme_river,heatmap,calendar_heatmap等

### API使用举例

#### echartspy.express包  pandas DataFrame 可视化

```python
from echartspy import Echarts,Tools
import echartspy.express as ex
import pandas as pd
df = pd.DataFrame(
    {
       '水果':['苹果','梨','草莓','香蕉'],
       '数量':[3,2,5,4],
       '价格':[10,9,8,5],
       '类别':['硬','硬','软','软']
    })
```

```python
ex.scatter(df,x='数量',y='价格',size='数量',group='水果',size_max=50,height='250px',title='scatter').render_notebook()
```

```python
ex.line(df,x='水果',y='价格',title="line",height='250px').render_notebook()
```

```python
ex.bar(df,x='水果',y='价格',group='类别',title="bar2",height='250px').render_notebook()
```

```python
ex.pie(df,name='水果',value='数量',rose_type='area',title="pie2",height='350px').render_notebook()
```

```python
ex.line(df,x='水果',y='价格',title="line",height='250px').render_notebook()
```

```python
from stocksdk import *
df=api.get_price("000001.XSHE") # 包含 time,open,high,low,close,volume 这些列
ex.candlestick(df.reset_index(),left='5%',mas=[5,10,30],title='平安银行').render_notebook()
```

#### Tools工具API使用

工具函数都是Tools类的静态方法

##### JavaScript配置自动转换成python配置
```python
from echartspy import Echarts,Tools
js_str="""
{
    xAxis: {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    yAxis: {
        type: 'value'
    },
    series: [{
        data: [820, 932, 901, 934, 1290, 1330, 1320],
        type: 'line',
        smooth: true
    }]
}
"""
options=Tools.convert_js_to_dict(js_str,print_dict=False)
```

##### DataFrame Series ndarray 转换成list类型

```python
import pandas as pd
from echartspy import Tools
df = pd.DataFrame(
    {
       '水果':['苹果','梨','草莓','香蕉'],
       '数量':[3,2,5,4],
       '价格':[10,9,8,5],
       '类别':['硬','硬','软','软']
    })
list_data = Tools.convert_to_list(df)
```

##### 模板工具方法
封装了jinja2,主要用于Js函数

```python
from echartspy import Tools
max_size_value = 100
size_max =30
# **locals() 是上下文变量词典，这是偷懒的写法， 也可以命名参数方式传递: max_size_value=max_size_value,size_max=size_max
Tools.wrap_template(
"""
    function(val) {
     return val[2]/{{max_size_value}}*{{size_max}};
    }
""", **locals())
```

