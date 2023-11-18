// @ts-nocheck
import "./ConsistencyView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js';

const BoxPlot = ({ url, traceFolder }) => {
    const [plotInput, setPlotInput] = useState([]);

    const fetchData = async (url) => {
        const response = await fetch(url, {
            headers: { accept: "application/json" },
            method: "GET"
        })
    
        if (!response.ok) throw new Error(response.status)
        var out = await response.json();
        setPlotInput(out);
        return response;
    }

    useEffect(() => {
        if (traceFolder) {
            fetchData(url)
        }
    }, [traceFolder])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    )
}

const ConsistencyView = ({ menu, traceFolder }) => {
    return (
        <>
            <BoxPlot traceFolder={traceFolder} url={`http://localhost:5000/consistency_AllReduce_start2start?folder=${traceFolder}`} />
            <BoxPlot traceFolder={traceFolder} url={`http://localhost:5000/consistency_AllReduce_start2end?folder=${traceFolder}`} />
            <BoxPlot traceFolder={traceFolder} url={`http://localhost:5000/consistency_AllGather_start2start?folder=${traceFolder}`} />
            <BoxPlot traceFolder={traceFolder} url={`http://localhost:5000/consistency_AllGather_start2end?folder=${traceFolder}`} />
            <BoxPlot traceFolder={traceFolder} url={`http://localhost:5000/consistency_ReduceScatter_start2start?folder=${traceFolder}`} />
            <BoxPlot traceFolder={traceFolder} url={`http://localhost:5000/consistency_ReduceScatter_start2end?folder=${traceFolder}`} />
        </>
    );
};

export default ConsistencyView;