#!/usr/bin/env python
# coding=utf-8
import copy
import os
import re
import uuid

import pandas as pd
import simplejson

from .base import Tools, GLOBAL_ENV, Html, json_type_convert, FUNCTION_BOUNDARY_MARK

G2PLOT_JS_URL: str = "https://cdn.staticfile.org/g2plot/2.4.1/g2plot.min.js"

# language=HTML
JUPYTER_ALL_TEMPLATE = """

<style>
  #{{plot.plot_id}} {
    width:{{plot.width}};
    height:{{plot.height}};
 }
</style>
<div id="{{ plot.plot_id }}"></div>
<script>
  {{plot.extra_js}}
  var options_{{ plot.plot_id }} = {{ plot.js_options }}
  if (typeof require !== 'undefined'){
      require.config({
        paths: {
          "G2Plot": "{{plot.js_url[:-3]}}"
        }
      });
      require(['G2Plot'], function (G2Plot) {
        var plot_{{ plot.plot_id }} = new G2Plot.{{plot.plot_type}}("{{ plot.plot_id }}", options_{{ plot.plot_id }}); 
        plot_{{ plot.plot_id }}.render();
      });
  }else{
    new Promise(function(resolve, reject) {
      var script = document.createElement("script");
      script.onload = resolve;
      script.onerror = reject;
      script.src = "{{plot.js_url}}";
      document.head.appendChild(script);
    }).then(() => {
       var plot_{{ plot.plot_id }} = new G2Plot.{{plot.plot_type}}("{{ plot.plot_id }}", options_{{ plot.plot_id }}); 
       plot_{{ plot.plot_id }}.render();
    });
  }

</script>
"""

# language=HTML
JUPYTER_NOTEBOOK_TEMPLATE = """
<script>
  require.config({
    paths: {
      "G2Plot": "{{plot.js_url[:-3]}}"
    }
  });
</script>
<style>
  #{{plot.plot_id}} {
    width:{{plot.width}};
    height:{{plot.height}};
 }
</style>
<div id="{{ plot.plot_id }}"></div>
<script>
  {{plot.extra_js}}
  require(['G2Plot'], function (G2Plot) {
    var plot_{{ plot.plot_id }} = new G2Plot.{{plot.plot_type}}("{{ plot.plot_id }}", {{ plot.js_options }}) 
    plot_{{ plot.plot_id }}.render();
  });
</script>

"""

# language=HTML
JUPYTER_LAB_TEMPLATE = """
<style>
 #{{plot.plot_id}} {
    width:{{plot.width}};
    height:{{plot.height}};
 }
</style>
<div id="{{ plot.plot_id }}"></div>
<script>
// load javascript

{{plot.extra_js}}
new Promise(function(resolve, reject) {
  var script = document.createElement("script");
  script.onload = resolve;
  script.onerror = reject;
  script.src = "{{plot.js_url}}";
  document.head.appendChild(script);
}).then(() => {
  var plot_{{ plot.plot_id }} = new G2Plot.{{plot.plot_type}}("{{ plot.plot_id }}", {{ plot.js_options }}) 
  plot_{{ plot.plot_id }}.render();
});
</script>
"""

# language=HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title></title>
    <style>
      #{{plot.plot_id}} {
            width:{{plot.width}};
            height:{{plot.height}};
         }
    </style>
   <script type="text/javascript" src="{{ plot.js_url }}"></script>
</head>
<body>
  <div id="{{ plot.plot_id }}" ></div>
  <script>
     {{plot.extra_js}}
     var plot_{{ plot.plot_id }} = new G2Plot.{{plot.plot_type}}("{{ plot.plot_id }}", {{ plot.js_options }}) 
     plot_{{ plot.plot_id }}.render();
  </script>
</body>
</html>
"""

# language=HTML
HTML_FRAGMENT_TEMPLATE = """
<div>
 <script type="text/javascript" src="{{ plot.js_url }}"></script>
 <style>
      #{{plot.plot_id}} {
            width:{{plot.width}};
            height:{{plot.height}};
         }
 </style>
 <div id="{{ plot.plot_id }}" ></div>
  <script>
    {{plot.extra_js}}
    var plot_{{ plot.plot_id }} = new G2Plot.{{plot.plot_type}}("{{ plot.plot_id }}", {{ plot.js_options }}) 
    plot_{{ plot.plot_id }}.render();
  </script>
</div>
"""


class G2PLOT(object):
    """
    g2plot
    """

    def __init__(self, data=None, plot_type: str = None, options: dict = None, extra_js: str = "", width: str = "100%",
                 height: str = "500px"):
        """
        :param options: python词典类型的echarts option
        :param extra_js: 复杂图表需要声明定义额外js函数的，通过这个字段传递
        :param width: 输出div的宽度 支持像素和百分比 比如800px/100%
        :param height: 输出div的高度 支持像素和百分比 比如800px/100%
        """
        if isinstance(data, pd.DataFrame):
            data = data.reset_index().to_dict(orient='records')
        self.options = options
        self.options['data'] = data
        self.plot_type = plot_type
        self.js_options = ""
        self.width = width
        self.height = height
        self.plot_id = "u" + uuid.uuid4().hex
        self.js_url = G2PLOT_JS_URL
        self.extra_js = extra_js

    def line(self, x_field=None, y_field=None, series_field=None):
        self.plot_type = "Line"
        self.options['xField'] = x_field
        self.options['yField'] = y_field
        if series_field is not None:
            self.options['seriesField'] = series_field
        return self

    def scatter(self, x_field=None, y_field=None, color_field=None, size_field=None, shape_field=None):
        self.plot_type = "Scatter"
        self.options['xField'] = x_field
        self.options['yField'] = y_field
        if color_field is not None:
            self.options['colorField'] = color_field
        if size_field is not None:
            self.options['sizeField'] = size_field
        if shape_field is not None:
            self.options['shapeField'] = shape_field
        return self

    def area(self, x_field=None, y_field=None, series_field=None):
        self.plot_type = "Area"
        self.options['xField'] = x_field
        self.options['yField'] = y_field
        if series_field is not None:
            self.options['seriesField'] = series_field
        return self

    def column(self, x_field=None, y_field=None, series_field=None, is_stack=False, is_group=False, is_range=False):
        self.plot_type = "Column"
        self.options['xField'] = x_field
        self.options['yField'] = y_field
        if series_field is not None:
            self.options['seriesField'] = series_field
        if is_stack:
            self.options['isStack'] = True
        elif is_group:
            self.options['isGroup'] = True
        elif is_range:
            self.options['isRange'] = True
        return self

    def rose(self, x_field=None, y_field=None, series_field=None, is_stack=False, is_group=False):
        self.plot_type = "Rose"
        self.options['xField'] = x_field
        self.options['yField'] = y_field
        if series_field is not None:
            self.options['seriesField'] = series_field
        if is_stack:
            self.options['isStack'] = True
        elif is_group:
            self.options['isGroup'] = True
        return self

    def pie(self, angle_field=None, color_field=None):
        self.plot_type = "Pie"
        self.options['angleField'] = angle_field
        self.options['colorField'] = color_field
        return self

    def gauge(self, percent=0.25):
        self.plot_type = "Gauge"
        self.options['percent'] = percent
        return self

    def liquid(self, percent=0.25):
        self.plot_type = "Liquid"
        self.options['percent'] = percent
        return self

    def bullet(self, measure_field=[100], range_field=[60, 80, 90], target_field=100, title=""):
        self.plot_type = "Bullet"
        self.options['measureField'] = measure_field
        self.options['rangeField'] = range_field
        self.options['targetField'] = target_field
        self.options['xField'] = title
        return self

    def sankey(self, source_field=None, target_field=None, weight_field=None):
        self.plot_type = "Sankey"
        self.options['sourceField'] = source_field
        self.options['targetField'] = target_field
        self.options['weightField'] = weight_field
        return self

    def chord(self, source_field=None, target_field=None, weight_field=None):
        self.plot_type = "Chord"
        self.options['sourceField'] = source_field
        self.options['targetField'] = target_field
        self.options['weightField'] = weight_field
        return self

    def heatmap(self, x_field=None, y_field=None, color_field=None):
        self.plot_type = "Heatmap"
        self.options['xField'] = x_field
        self.options['yField'] = y_field
        self.options['colorField'] = color_field
        self.options["meta"]: {
            x_field: {
                'type': 'cat'
            },
            y_field: {
                'type': 'cat'
            },
        }
        return self

    def radar(self, x_field=None, y_field=None):
        self.plot_type = "Radar"
        self.options['xField'] = x_field
        self.options['yField'] = y_field
        self.options['area'] = {}

    def print_options(self, drop_data=False):
        """
        格式化打印options 方便二次修改
        :param drop_data: 是否过滤掉data，减小打印长度，方便粘贴
        :return:
        """
        dict_options = copy.deepcopy(self.options)
        if drop_data:
            series_count = len(dict_options['series'])
            for i in range(0, series_count):
                dict_options['series'][i]['data'] = []
        Tools.convert_js_to_dict(Tools.convert_dict_to_js(dict_options), print_dict=True)

    def dump_options(self):
        """
         导出 js option字符串表示
        :return:
        """
        self.js_options = Tools.convert_dict_to_js(self.options)
        return self.js_options

    def render_notebook(self) -> Html:
        """
        在jupyter notebook 环境输出
        :return:
        """
        self.js_options = Tools.convert_dict_to_js(self.options)
        html = GLOBAL_ENV.from_string(JUPYTER_NOTEBOOK_TEMPLATE).render(plot=self)
        return Html(html)

    def render_jupyterlab(self) -> Html:
        """
        在jupyterlab 环境输出
        :return:
        """
        self.js_options = Tools.convert_dict_to_js(self.options)
        html = GLOBAL_ENV.from_string(JUPYTER_LAB_TEMPLATE).render(plot=self)
        return Html(html)

    def render_file(self, path: str = "plot.html") -> Html:
        """
        输出html到文件
        :param path:
        :return: 文件路径
        """
        self.js_options = Tools.convert_dict_to_js(self.options)
        html = GLOBAL_ENV.from_string(HTML_TEMPLATE).render(plot=self)
        with open(path, "w+", encoding="utf-8") as html_file:
            html_file.write(html)
        abs_path = os.path.abspath(path)
        return Html("<p>{path}</p>".format(path=abs_path))

    def render_html(self) -> str:
        """
        渲染html字符串，可以用于 streamlit
        :return:
        """
        self.js_options = Tools.convert_dict_to_js(self.options)
        html = GLOBAL_ENV.from_string(HTML_TEMPLATE).render(plot=self)
        return html

    def render_html_fragment(self):
        """
        渲染html 片段，方便一个网页输出多个图表
        :return:
        """
        self.js_options = Tools.convert_dict_to_js(self.options)
        html = GLOBAL_ENV.from_string(HTML_FRAGMENT_TEMPLATE).render(plot=self)
        return html

    def _repr_html_(self):
        """
        jupyter 环境，直接输出
        :return:
        """
        self.js_options = Tools.convert_dict_to_js(self.options)
        html = GLOBAL_ENV.from_string(JUPYTER_ALL_TEMPLATE).render(plot=self)
        return Html(html).data
