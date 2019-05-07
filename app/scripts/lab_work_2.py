import operator
import statistics

import numpy as np
from bokeh.embed import components
from bokeh.models import (
    Arrow,
    ColumnDataSource,
    HoverTool,
    LabelSet,
    NormalHead,
    Span
)
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from flask import redirect, render_template, request, url_for

from app import app
from app.scripts.helpers import *


def cnt_in_range(list, range, x):
    cnt = 0
    for k, v in list.items():
        if x > 0:
            if range[0] < k and k <= range[1]:
                cnt = cnt + v
        else:
            if range[0] <= k and k <= range[1]:
                cnt = cnt + v

    return cnt


def get_histogram(h, src):
    p = figure(
        height=600,
        sizing_mode='stretch_width',
        x_axis_label='I',
        y_axis_label='N / %s' % str(h)
    )

    p.quad(
        source=src,
        bottom=0,
        top='t',
        left='l',
        right='r',
        line_color='black'
    )

    h = HoverTool(tooltips=[
        ('N / %s ' % str(h), '@t{1.111}'),
        ('start; end', '@l; @r')
    ])

    p.add_tools(h)

    return p


@app.route('/lab_work_2', methods=['POST'])
def lab_work_2_post():
    sti = []
    cnt = w_nak = 0
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    items, res = get_input_data()

    mode = [k for k, v in res.items() if v == max(res.values())]
    median = statistics.median(items)

    h = to_int_if_can(request.form['h'])
    ranges = list(map(to_int_if_can, np.arange(min(items), max(items)+h, h)))

    st = get_stat_distr(res)

    for x in range(0, len(ranges)-1):
        interval = (round(ranges[x], 3), round(ranges[x+1], 3))
        n = cnt_in_range(res, interval, x)
        cnt = cnt + n
        w_nak = round(cnt / len(items), 3)

        sti.append({
            'i': interval,
            'n': n,
            'w': round(n / len(items), 3),
            'n_nak': cnt,
            'w_nak': w_nak
        })

    src = {'t': [], 'l': [], 'r': []}

    for x in sti:
        src.get('t').append(x.get('n')/h)
        src.get('l').append(x.get('i')[0])
        src.get('r').append(x.get('i')[1])

    fig1 = get_histogram(h, ColumnDataSource(src))
    plot_1 = {}
    plot_1['script'], plot_1['div'] = components(fig1)

    src2 = ColumnDataSource({
        't': [round(x.get('w')/h, 3) for x in sti],
        'l': [x.get('i')[0] for x in sti],
        'r': [x.get('i')[1] for x in sti]
    })

    fig2 = get_histogram(h, src2)
    plot_2 = {}
    plot_2['script'], plot_2['div'] = components(fig2)

    x = [sti[0].get('i')[0]]
    y = [0]
    for e in sti:
        x.append(e.get('i')[1])
    for e in sti:
        y.append(e.get('w_nak'))

    fig3 = get_figure(x, y, 'X', 'F*(x)')
    plot_3 = {}
    plot_3['script'], plot_3['div'] = components(fig3)

    html = render_template(
        'lab_work_2/lab_work_2_res.html',
        action_url='/lab_work_2',
        mode=", ".join([str(m) for m in mode]),
        median=to_int_if_can(median),
        items=items,
        h=h,
        st=st,
        sti=sti,
        plot_1=plot_1,
        plot_2=plot_2,
        plot_3=plot_3,
        js_resources=js_resources,
        css_resources=css_resources,
    )
    return encode_utf8(html)


@app.route('/lab_work_2', methods=['GET'])
def lab_work_2_get():
    html = render_template(
        'lab_work_2/lab_work_2.html',
        action_url='/lab_work_2'
    )
    return encode_utf8(html)
