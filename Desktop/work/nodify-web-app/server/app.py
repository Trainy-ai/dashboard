# app.py
from flask import Flask, render_template, jsonify, request, make_response, Response
from flask_cors import CORS

from hta.trace_analysis import TraceAnalysis

import numpy as np
import pandas as pd
import os
import json

from functools import cache

import plotly
import plotly.express as px
import sys


import socket

## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()

from utils.plot import (
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

all_trace_analyzers = {}

a = os.listdir('/')

b = os.listdir('/traces/')

print(a)
print(b)

"""
for item in os.listdir("/traces/"):
    newItem = os.path.join("/traces/", item)
    all_trace_analyzers[item] = TraceAnalysis(trace_dir=newItem)
"""
"""
class ActiveTrace:
    logdir = "/traces/"
    trace_analyzer = TraceAnalysis(trace_dir=logdir)
    trace_analysis = os.listdir(logdir)[0]

try:
    trace_analyzer = TraceAnalysis(trace_dir=logdir)
except ValueError as e:
    print(
        f"An exception occurred loading your trace files. You will not be able to visualize anything: {str(e)}"
    )
"""

@app.route('/traces', methods=['GET'])
def traces_route():
    traces = os.listdir("/traces/")
    return json.dumps({"traces": traces})

@app.route('/num_ranks', methods=['GET'])
def num_ranks_route():
    folder = request.args.get('folder')
    num_ranks = len(all_trace_analyzers[folder].t.traces)
    return json.dumps({"num_ranks": num_ranks})

@app.route('/idle_time', methods=['GET'])
def idle_time_route():
    folder = request.args.get('folder')
    rank = request.args.get('rank')
    pct = request.args.get('visualizePct')
    pct_bool = pct == 'true'

    # Replace self.trace_analyzer with the instantiated TraceAnalysis object
    idle_time_df = all_trace_analyzers[folder].get_idle_time_breakdown(
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

@app.route('/temporal_dev', methods=['GET'])
def temporal_dev():
    folder = request.args.get('folder')
    time_spent_df = all_trace_analyzers[folder].get_temporal_breakdown(visualize=False)
    contents = time_spent_df.to_json()
    return contents

@app.route('/temporal', methods=['GET'])
def temporal_breakdown_route():

    folder = request.args.get('folder')
    time_spent_df = all_trace_analyzers[folder].get_temporal_breakdown(visualize=False)
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

@app.route('/kernel', methods=['GET'])
def kernel_route():
    folder = request.args.get('folder')
    # TODO: Refactor this to split the dataframe logic from the plotting logic for the later plots
    (
        kernel_type_df,
        kernel_metrics_df,
    ) = all_trace_analyzers[folder].get_gpu_kernel_breakdown(visualize=False)
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

@app.route('/consistency_AllReduce_start2start', methods=['GET'])
def consistency_AllReduce_start2start_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_AllReduce"
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

@app.route('/consistency_ReduceScatter_start2start', methods=['GET'])
def consistency_ReduceScatter_start2start_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_ReduceScatter"
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

@app.route('/consistency_AllGather_start2start', methods=['GET'])
def consistency_AllGather_start2start_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_AllGather"
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

@app.route('/consistency_AllReduce_start2end', methods=['GET'])
def consistency_AllReduce_start2end_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start2end(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_AllReduce"
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

@app.route('/consistency_ReduceScatter_start2end', methods=['GET'])
def consistency_ReduceScatter_start2end_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start2end(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_ReduceScatter"
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

@app.route('/consistency_AllGather_start2end', methods=['GET'])
def consistency_AllGather_start2end_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start2end(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_AllGather"
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

@app.route('/progress_AllReduce_start2start', methods=['GET'])
def progress_AllReduce_start2start_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_AllReduce"
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

@app.route('/progress_ReduceScatter_start2start', methods=['GET'])
def progress_ReduceScatter_start2start_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_ReduceScatter"
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

@app.route('/progress_AllGather_start2start', methods=['GET'])
def progress_AllGather_start2start_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_AllGather"
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

@app.route('/progress_AllReduce_start2end', methods=['GET'])
def progress_AllReduce_start2end_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start2end(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_AllReduce"
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

@app.route('/progress_ReduceScatter_start2end', methods=['GET'])
def progress_ReduceScatter_start2end_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start2end(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_ReduceScatter"
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

@app.route('/progress_AllGather_start2end', methods=['GET'])
def progress_AllGather_start2end_route():
    folder = request.args.get('folder')

    df = time_between_barriers_start2end(
        all_trace_analyzers[folder].t, comm_id="ncclKernel_AllGather"
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

@app.route('/util_heat', methods=['GET'])
def util_heat_route():
      # unused
    folder = request.args.get('folder')

    fraction, bins = heatmap(all_trace_analyzers[folder].t, bins=30, type="compute")
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

@app.route('/comm_heat', methods=['GET'])
def comm_heat_route():
      # unused
    folder = request.args.get('folder')

    fraction, bins = heatmap(all_trace_analyzers[folder].t, bins=30, type="comm")
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

@app.route('/mem_heat', methods=['GET'])
def mem_heat_route():
      # unused
    folder = request.args.get('folder')

    fraction, bins = heatmap(all_trace_analyzers[folder].t, bins=30, type="mem")
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

@app.route('/compute_communication_overlap', methods=['GET'])
@cache
def compute_communication_overlap_route():
    folder = request.args.get('folder')

    try:
        result_df = all_trace_analyzers[folder].get_comm_comp_overlap(visualize=False)
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
