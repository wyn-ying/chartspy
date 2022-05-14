#!/usr/bin/env python
# coding=utf-8
import copy
import os
import uuid

from .base import Tools, GLOBAL_ENV, Html

ECHARTS_JS_URL = "https://cdn.staticfile.org/echarts/5.3.2/echarts.min.js"
ECHARTS_GL_JS_URL = "https://cdn.staticfile.org/echarts-gl/2.0.8/echarts-gl.min.js"

# language=HTML
JUPYTER_ALL_TEMPLATE = """
<script>

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
  var options_{{ plot.plot_id }} = {{ plot.js_options }};
  if (typeof require !== 'undefined'){
    {% if plot.with_gl %}
      require.config({
        paths: {
          "echarts": "{{plot.js_url[:-3]}}",
          "echartsgl": "{{plot.js_url_gl[:-3]}}"
        }
      });
      require(['echarts','echartsgl'], function (echarts,echartsgl) {
        var plot_{{ plot.plot_id }} = echarts.init(document.getElementById('{{ plot.plot_id }}'));
        plot_{{ plot.plot_id }}.setOption(options_{{ plot.plot_id }})
      });
    {% else %}
      require.config({
        paths: {
          "echarts": "{{plot.js_url[:-3]}}",
        }
      });
      require(['echarts'], function (echarts) {
        var plot_{{ plot.plot_id }} = echarts.init(document.getElementById('{{ plot.plot_id }}'));
        plot_{{ plot.plot_id }}.setOption(options_{{ plot.plot_id }})
      });
    {% endif %}
    
      
  }else{
    new Promise(function(resolve, reject) {
      var script = document.createElement("script");
      script.onload = resolve;
      script.onerror = reject;
      script.src = "{{plot.js_url}}";
      document.head.appendChild(script);
      {% if plot.with_gl %}
          var scriptGL = document.createElement("script");
          scriptGL.onload = resolve;
          scriptGL.onerror = reject;
          scriptGL.src = "{{plot.js_url_gl}}";
          document.head.appendChild(scriptGL);
      {% endif %}

    }).then(() => {
       var plot_{{ plot.plot_id }} = echarts.init(document.getElementById('{{ plot.plot_id }}'));
       plot_{{ plot.plot_id }}.setOption(options_{{ plot.plot_id }})
    });
  }

</script>
"""

# language=HTML
JUPYTER_NOTEBOOK_TEMPLATE = """

<style>
  #{{plot.plot_id}} {
    width:{{plot.width}};
    height:{{plot.height}};
 }
</style>
<div id="{{ plot.plot_id }}"></div>
<script>
    {% if plot.with_gl %}
      require.config({
        paths: {
          "echarts": "{{plot.js_url[:-3]}}",
          "echartsgl": "{{plot.js_url_gl[:-3]}}"
        }
      });
      require(['echarts','echartsgl'], function (echarts,echartsgl) {
        var plot_{{ plot.plot_id }} = echarts.init(document.getElementById('{{ plot.plot_id }}'));
        {{plot.extra_js}}
        var options_{{ plot.plot_id }} = {{ plot.js_options }};
        plot_{{ plot.plot_id }}.setOption(options_{{ plot.plot_id }})
      });
    {% else %}
      require.config({
        paths: {
          "echarts": "{{plot.js_url[:-3]}}",
        }
      });
      require(['echarts'], function (echarts) {
        var plot_{{ plot.plot_id }} = echarts.init(document.getElementById('{{ plot.plot_id }}'));
        {{plot.extra_js}}
        var options_{{ plot.plot_id }} = {{ plot.js_options }};
        plot_{{ plot.plot_id }}.setOption(options_{{ plot.plot_id }})
      });
    {% endif %}
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
    new Promise(function(resolve, reject) {
      var script = document.createElement("script");
      script.onload = resolve;
      script.onerror = reject;
      script.src = "{{plot.js_url}}";
      document.head.appendChild(script);
      {% if plot.with_gl %}
      var scriptGL = document.createElement("script");
      scriptGL.onload = resolve;
      scriptGL.onerror = reject;
      scriptGL.src = "{{plot.js_url_gl}}";
      document.head.appendChild(scriptGL);
      {% endif %}
    }).then(() => {
       var plot_{{ plot.plot_id }} = echarts.init(document.getElementById('{{ plot.plot_id }}'));
       {{plot.extra_js}}
       plot_{{ plot.plot_id }}.setOption({{ plot.js_options }})
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
   {% if plot.with_gl %}
    <script type="text/javascript" src="{{ plot.js_url_gl }}"></script>
   {% endif %}
</head>
<body>
  <div id="{{ plot.plot_id }}" ></div>
  <script>
    var plot_{{ plot.plot_id }} = echarts.init(document.getElementById('{{ plot.plot_id }}'));
    {{plot.extra_js}}
    plot_{{ plot.plot_id }}.setOption({{ plot.js_options }})
  </script>
</body>
</html>
"""

# language=HTML
HTML_FRAGMENT_TEMPLATE = """
<div>
 <script type="text/javascript" src="{{ plot.js_url }}"></script>
   {% if plot.with_gl %}
    <script type="text/javascript" src="{{ plot.js_url_gl }}"></script>
   {% endif %}
 <style>
      #{{plot.plot_id}} {
            width:{{plot.width}};
            height:{{plot.height}};
         }
 </style>
 <div id="{{ plot.plot_id }}" ></div>
  <script>
    var plot_{{ plot.plot_id }} = echarts.init(document.getElementById('{{ plot.plot_id }}'));
    {{plot.extra_js}}
    plot_{{ plot.plot_id }}.setOption({{ plot.js_options }})
  </script>
</div>
"""


class Echarts(object):
    """
    echarts
    """

    def __init__(self, options: dict = None, extra_js: str = "", with_gl=False, width: str = "100%",
                 height: str = "500px"):
        """
        :param options: python词典类型的echarts option
        :param extra_js: 复杂图表需要声明定义额外js函数的，通过这个字段传递
        :param width: 输出div的宽度 支持像素和百分比 比如800px/100%
        :param height: 输出div的高度 支持像素和百分比 比如800px/100%
        """
        self.options = options
        self.js_options = ""
        self.width = width
        self.height = height
        self.plot_id = "u" + uuid.uuid4().hex
        self.js_url = ECHARTS_JS_URL
        self.js_url_gl = ECHARTS_GL_JS_URL
        self.extra_js = extra_js
        self.with_gl = with_gl

    @staticmethod
    def timeline(echarts_dict: dict = {}, visual_map_options=None):
        """

        :param echarts_dict: key类型字符串，用作标题, value类型 Echarts对象，或者Echarts对象的options
        :param visual_map_options: visualMap 配置,visualMap最大值最小值需要配置的时候设置,格式参照echarts官方文档
        :return:
        """
        charts_dict = {k: (v.options if isinstance(v, Echarts) else v) for k, v in echarts_dict.items()}
        options = {
            "baseOption": {
                'timeline': {
                    'axisType': 'category',
                    'orient': 'vertical',
                    'autoPlay': True,
                    'inverse': True,
                    'playInterval': 1000,
                    'left': None,
                    'right': 0,
                    'top': 20,
                    'bottom': 20,
                    'width': 55,
                    'height': None,
                    'symbol': 'none',
                    'checkpointStyle': {
                        'borderWidth': 2
                    },
                    'controlStyle': {
                        'showNextBtn': False,
                        'showPrevBtn': False
                    },
                    'data': [],
                },
                'grid': {
                    'top': 100,
                    'containLabel': True,
                    'left': 30,
                    'right': '110'
                },
                'animationDurationUpdate': 1000,
                'animationEasingUpdate': 'quinticInOut'
            },
            'options': []
        }
        keys = list(charts_dict.keys())
        keys.sort()
        options['baseOption']['timeline']['data'] = keys
        if len(keys) > 0:
            if 'tooltip' in charts_dict[keys[0]].keys():
                options['baseOption']['tooltip'] = charts_dict[keys[0]]['tooltip']
            if 'xAxis' in charts_dict[keys[0]].keys():
                options['baseOption']['xAxis'] = charts_dict[keys[0]]['xAxis']
            if 'yAxis' in charts_dict[keys[0]].keys():
                options['baseOption']['yAxis'] = charts_dict[keys[0]]['yAxis']

            if visual_map_options is not None:
                options['baseOption']['visualMap'] = visual_map_options
            elif 'visualMap' in charts_dict[keys[0]].keys():
                options['baseOption']['visualMap'] = charts_dict[keys[0]]['visualMap']
            if 'series' in charts_dict[keys[0]].keys():
                options['baseOption']['series'] = charts_dict[keys[0]]['series']
            for i in range(0, len(keys)):
                options['options'].append({
                    'title': {
                        'show': True,
                        'text': keys[i]
                    },
                    'series': charts_dict[keys[i]]['series']
                })
                if 'visualMap' in charts_dict[keys[i]].keys() and 'visualMap' in options['baseOption'].keys():
                    if isinstance(charts_dict[keys[i]]['visualMap'], list) and isinstance(
                            options['baseOption']['visualMap'], list) and len(charts_dict[keys[i]]['visualMap']) == len(options['baseOption']['visualMap']):
                        for j in range(0, len(options['baseOption']['visualMap'])):
                            if 'min' in options['baseOption']['visualMap'][j].keys():
                                options['baseOption']['visualMap'][j]['min'] = min(
                                    options['baseOption']['visualMap'][j]['min'],
                                    charts_dict[keys[i]]['visualMap'][j]['min'])
                            if 'max' in options['baseOption']['visualMap'][j].keys():
                                options['baseOption']['visualMap'][j]['max'] = min(
                                    options['baseOption']['visualMap'][j]['max'],
                                    charts_dict[keys[i]]['visualMap'][j]['max'])
                    elif isinstance(charts_dict[keys[i]]['visualMap'], dict) and isinstance(
                            options['baseOption']['visualMap'], dict):
                        if 'min' in options['baseOption']['visualMap'].keys():
                            options['baseOption']['visualMap']['min'] = min(
                                options['baseOption']['visualMap']['min'],
                                charts_dict[keys[i]]['visualMap']['min'])
                        if 'max' in options['baseOption']['visualMap'].keys():
                            options['baseOption']['visualMap']['max'] = max(
                                options['baseOption']['visualMap']['max'],
                                charts_dict[keys[i]]['visualMap']['max'])

        return Echarts(options=options)

    def overlap_series(self, other_chart_options: list = []):
        """
        叠加其他配置中的Series数据到现有配置，现有配置有多个坐标轴的，建议Series声明对应的axisIndex
        :param other_chart_options:要叠加的Echarts对象列表，或者options列表
        :return:
        """
        this_options = copy.deepcopy(self.options)
        if this_options["legend"]["data"] is None:
            this_options["legend"]["data"] = []
        if this_options["series"] is None:
            this_options["series"] = []

        for chart_option in other_chart_options:
            if isinstance(chart_option, Echarts):
                chart_option = chart_option.options
            old_series_count = len(this_options["series"])
            this_options["legend"]["data"].extend(chart_option["legend"]["data"])
            this_options["series"].extend(chart_option["series"])
            if "visualMap" in chart_option.keys():
                if "visualMap" not in this_options.keys():
                    this_options["visualMap"] = []
                for i in range(0, len(chart_option["visualMap"])):
                    if "seriesIndex" in chart_option["visualMap"][i].keys():
                        chart_option["visualMap"][i]['seriesIndex'] = chart_option["visualMap"][i][
                                                                          'seriesIndex'] + old_series_count
                    else:
                        chart_option["visualMap"][i]['seriesIndex'] = old_series_count
                this_options["visualMap"].extend(chart_option["visualMap"])
        return Echarts(options=this_options, extra_js=self.extra_js, width=self.width, height=self.height)

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
