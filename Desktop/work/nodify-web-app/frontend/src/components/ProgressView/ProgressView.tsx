// @ts-nocheck
import "./ProgressView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js';

const fetchData = async ({ setPlotInput }, url) => {
    const response = await fetch(url, {
        headers: { accept: "application/json" },
    })

    if (!response.ok) throw new Error(response.status)
    var out = await response.json();
    setPlotInput(out);
    return response;
}

const BoxPlot = ({ url }) => {
    const [plotInput, setPlotInput] = useState([]);

    useEffect(() => {
        fetchData({ setPlotInput }, url);
    }, [])
    
    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    )
}

const ProgressView = ({ menu }) => {
    return (
        <>
            <BoxPlot url="http://localhost:5000/progress_AllReduce_start2start" />
            <BoxPlot url="http://localhost:5000/progress_AllReduce_start2end" />
            <BoxPlot url="http://localhost:5000/progress_AllGather_start2start" />
            <BoxPlot url="http://localhost:5000/progress_AllGather_start2end" />
            <BoxPlot url="http://localhost:5000/progress_ReduceScatter_start2start" />
            <BoxPlot url="http://localhost:5000/progress_ReduceScatter_start2end" />
        </>
    );
};

export default ProgressView;