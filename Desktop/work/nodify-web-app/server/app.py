# app.py
from flask import Flask, render_template, jsonify, request, make_response, Response
from flask_cors import CORS

from hta.trace_analysis import TraceAnalysis

import numpy as np
import pandas as pd
import os
import json
import sys

from functools import cache
from datetime import datetime

import plotly
import plotly.express as px

from tensorboard.plugins import base_plugin

import socket

## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()

from nodify_plugin.utils.plot import (
    heatmap,
    time_between_barriers_start,
    time_between_barriers_start2end,
    box_plot,
    empty_plot
)

PLUGIN_NAME = "nodify_plugin"

plugin_name = PLUGIN_NAME
headers = [("X-Content-Type-Options", "nosniff")]

app = Flask(__name__)
CORS(app)

logdir = ""
trace_analyzer = None

class ActiveTrace:

    logdir = "/traces/"
    trace_analyzer = TraceAnalysis(trace_dir=logdir)
    trace_analysis = os.listdir(logdir)[0]

"""
if len(sys.argv) > 1:
    argument = sys.argv[1]
    logdir = os.path.abspath(argument.rstrip("/"))
else:
    print("No command-line argument provided.")
    quit

try:
    trace_analyzer = TraceAnalysis(trace_dir=logdir)
except ValueError as e:
    print(
        f"An exception occurred loading your trace files. You will not be able to visualize anything: {str(e)}"
    )
"""

@app.route('/num_ranks')
def num_ranks_route():
    num_ranks = len(trace_analyzer.t.traces)
    return json.dumps({"num_ranks": num_ranks})

@app.route('/idle_time')
def idle_time_route():
    rank = request.args.get('rank')
    pct = request.args.get('visualizePct')
    pct_bool = pct == 'true'

    # Replace self.trace_analyzer with the instantiated TraceAnalysis object
    idle_time_df = trace_analyzer.get_idle_time_breakdown(
        ranks=[int(rank)], visualize=False, visualize_pctg=pct_bool
    )[0]

    idle_time_df['stream'] = idle_time_df.stream.astype(str)
    ycol = 'idle_time_ratio' if pct_bool else 'idle_time'

    fig = px.bar(
        idle_time_df,
        x='stream',
        y=ycol,
        color='idle_category',
        hover_data=['idle_time', 'idle_time_ratio'],
        title=f'Idle time breakdown on rank {rank} per CUDA stream',
    )

    if pct_bool:
        fig.update_layout(
            yaxis_tickformat='.2%',
            yaxis_title='Percentage',
            legend_title='Idle Time Breakdown',
        )
    else:
        fig.update_layout(
            yaxis_title='Idle time (us)',
            legend_title='Idle Time Breakdown',
        )

    contents = plotly.io.to_json(fig)
    return contents

@app.route('/temporal_dev')
def temporal_dev():
    time_spent_df = trace_analyzer.get_temporal_breakdown(visualize=False)
    contents = time_spent_df.to_json()
    return contents

@app.route('/temporal')
def temporal_breakdown_route():
    time_spent_df = trace_analyzer.get_temporal_breakdown(visualize=False)
    fig = px.bar(
        time_spent_df,
        x="rank",
        y=["idle_time_pctg", "compute_time_pctg", "non_compute_time_pctg"],
        title="Temporal breakdown across ranks",
        labels={"rank": "Rank"},
    )
    fig.update_layout(
        yaxis_tickformat=".%",
        yaxis_title="Percentage",
        legend_title="Time Breakdown",
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/kernel')
def kernel_route():
    # TODO: Refactor this to split the dataframe logic from the plotting logic for the later plots
    (
        kernel_type_df,
        kernel_metrics_df,
    ) = trace_analyzer.get_gpu_kernel_breakdown(visualize=False)
    non_zero_kernel_df = kernel_type_df[(kernel_type_df["percentage"] > 0)]

    fig = px.pie(
        non_zero_kernel_df,
        values="percentage",
        names="kernel_type",
        height=500,
        title="Kernel Type Percentage Across All Ranks",
    )
    fig.update_layout(
        margin=dict(l=50, r=50, b=50, t=50),
        showlegend=True,
        legend=dict(yanchor="bottom", y=-0.4, xanchor="left", x=0),
    )

    contents = plotly.io.to_json(fig)
    return contents

@app.route('/consistency_AllReduce_start2start')
def consistency_AllReduce_start2start_route():
    

    df = time_between_barriers_start(
        trace_analyzer.t, comm_id="ncclKernel_AllReduce"
    )
    fig = box_plot(
        df,
        error_msg="No AllReduce operations found",
        x="rank",
        y="delta",
        color="iteration",
        title="time between ncclKernel_AllReduce starts",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/consistency_ReduceScatter_start2start')
def consistency_ReduceScatter_start2start_route():


    df = time_between_barriers_start(
        trace_analyzer.t, comm_id="ncclKernel_ReduceScatter"
    )
    fig = box_plot(
        df,
        error_msg="No ReduceScatter operations found",
        x="rank",
        y="delta",
        color="iteration",
        title="time between ncclKernel_ReduceScatter starts",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/consistency_AllGather_start2start')
def consistency_AllGather_start2start_route():
    

    df = time_between_barriers_start(
        trace_analyzer.t, comm_id="ncclKernel_AllGather"
    )
    fig = box_plot(
        df,
        error_msg="No AllGather operations found",
        x="rank",
        y="delta",
        color="iteration",
        title="time between ncclKernel_AllGather starts",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/consistency_AllReduce_start2end')
def consistency_AllReduce_start2end_route():
    

    df = time_between_barriers_start2end(
        trace_analyzer.t, comm_id="ncclKernel_AllReduce"
    )
    fig = box_plot(
        df,
        error_msg="No AllReduce operations found",
        x="rank",
        y="delta",
        color="iteration",
        title="time between ncclKernel_AllReduce calls",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/consistency_ReduceScatter_start2end')
def consistency_ReduceScatter_start2end_route():
    

    df = time_between_barriers_start2end(
        trace_analyzer.t, comm_id="ncclKernel_ReduceScatter"
    )
    fig = box_plot(
        df,
        error_msg="No ReduceScatter operations found",
        x="rank",
        y="delta",
        color="iteration",
        title="time between ncclKernel_ReduceScatter calls",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/consistency_AllGather_start2end')
def consistency_AllGather_start2end_route():
    

    df = time_between_barriers_start2end(
        trace_analyzer.t, comm_id="ncclKernel_AllGather"
    )
    fig = box_plot(
        df,
        error_msg="No AllGather operations found",
        x="rank",
        y="delta",
        color="iteration",
        title="time between ncclKernel_AllGather calls",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/progress_AllReduce_start2start')
def progress_AllReduce_start2start_route():
    

    df = time_between_barriers_start(
        trace_analyzer.t, comm_id="ncclKernel_AllReduce"
    )
    fig = box_plot(
        df,
        error_msg="No AllReduce operations found",
        x="iteration",
        y="delta",
        color="rank",
        title="time between ncclKernel_AllReduce starts",
        labels={"delta": "time delta (ns)"},            
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/progress_ReduceScatter_start2start')
def progress_ReduceScatter_start2start_route():
    

    df = time_between_barriers_start(
        trace_analyzer.t, comm_id="ncclKernel_ReduceScatter"
    )

    fig = box_plot(
        df,
        error_msg="No ReduceScatter operations found",
        x="iteration",
        y="delta",
        color="rank",
        title="time between ncclKernel_ReduceScatter starts",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/progress_AllGather_start2start')
def progress_AllGather_start2start_route():
    

    df = time_between_barriers_start(
        trace_analyzer.t, comm_id="ncclKernel_AllGather"
    )
    fig = box_plot(
        df,
        error_msg="No AllGather operations found",
        x="iteration",
        y="delta",
        color="rank",
        title="time between ncclKernel_AllGather starts",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/progress_AllReduce_start2end')
def progress_AllReduce_start2end_route():
    

    df = time_between_barriers_start2end(
        trace_analyzer.t, comm_id="ncclKernel_AllReduce"
    )
    fig = box_plot(
        df,
        error_msg="No AllReduce operations found",
        x="iteration",
        y="delta",
        color="rank",
        title="time between ncclKernel_AllReduce calls",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/progress_ReduceScatter_start2end')
def progress_ReduceScatter_start2end_route():
    

    df = time_between_barriers_start2end(
        trace_analyzer.t, comm_id="ncclKernel_ReduceScatter"
    )
    fig = box_plot(
        df,
        error_msg="No ReduceScatter operations found",
        x="iteration",
        y="delta",
        color="rank",
        title="time between ncclKernel_ReduceScatter calls",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/progress_AllGather_start2end')
def progress_AllGather_start2end_route():
    

    df = time_between_barriers_start2end(
        trace_analyzer.t, comm_id="ncclKernel_AllGather"
    )
    fig = box_plot(
        df,
        error_msg="No AllGather operations found",
        x="iteration",
        y="delta",
        color="rank",
        title="time between ncclKernel_AllGather calls",
        labels={"delta": "time delta (ns)"},
    )
    contents = plotly.io.to_json(fig)
    return contents

@app.route('/util_heat')
def util_heat_route():
      # unused

    fraction, bins = heatmap(trace_analyzer.t, bins=30, type="compute")
    fraction = fraction.reset_index().rename(columns={0: "gpu_util"})
    fig = px.imshow(
        list(fraction["gpu_util"].values),
        labels=dict(x="Time (us)", y="rank", color="GPU Util"),
        y=fraction["rank"],
        title="% Time Computation",
    )

    fig.update_xaxes(
        tickangle=90,
        tickmode="array",
        tickvals=np.arange(len(bins)),
        ticktext=[d.strftime("%f") for d in pd.to_datetime(bins[:-1])],
    )

    contents = plotly.io.to_json(fig)
    return contents

@app.route('/comm_heat')
def comm_heat_route():
      # unused

    fraction, bins = heatmap(trace_analyzer.t, bins=30, type="comm")
    fraction = fraction.reset_index().rename(columns={0: "gpu_comm"})
    fig = px.imshow(
        list(fraction["gpu_comm"].values),
        labels=dict(x="Time (us)", y="rank", color="GPU Comm"),
        y=fraction["rank"],
        title="% Time Communication",
    )

    fig.update_xaxes(
        tickangle=90,
        tickmode="array",
        tickvals=np.arange(len(bins)),
        ticktext=[d.strftime("%f") for d in pd.to_datetime(bins[:-1])],
    )

    contents = plotly.io.to_json(fig)
    return contents

@app.route('/mem_heat')
def mem_heat_route():
      # unused

    fraction, bins = heatmap(trace_analyzer.t, bins=30, type="mem")
    fraction = fraction.reset_index().rename(columns={0: "gpu_mem"})
    fig = px.imshow(
        list(fraction["gpu_mem"].values),
        labels=dict(x="Time (us)", y="rank", color="GPU Mem"),
        y=fraction["rank"],
        title="% Time Memory",
    )

    fig.update_xaxes(
        tickangle=90,
        tickmode="array",
        tickvals=np.arange(len(bins)),
        ticktext=[d.strftime("%f") for d in pd.to_datetime(bins[:-1])],
    )

    contents = plotly.io.to_json(fig)
    return contents

@app.route('/compute_communication_overlap')
@cache
def compute_communication_overlap_route():
    

    try:
        result_df = trace_analyzer.get_comm_comp_overlap(visualize=False)
        fig = px.bar(
            result_df,
            x="rank",
            y="comp_comm_overlap_pctg",
            title="Computation-Communication Overlap",
            labels={
                "rank": "Rank",
                "comp_comm_overlap_pctg": "Computation-Communication Overlap Percentage",
            },
        )
    # No communication operations found
    except:
        fig = empty_plot("No communication operations found")

    contents = plotly.io.to_json(fig)
    return contents


if __name__ == "__main__":
    app.run(debug=True)
