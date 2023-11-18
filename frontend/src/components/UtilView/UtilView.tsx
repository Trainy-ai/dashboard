// @ts-nocheck
import "./UtilView.css";
import { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';

const fetchData = async ({ setPlotInput }, url) => {
    const response = await fetch(url, {
        headers: { accept: "application/json" },
        method: "GET"
    })

    if (!response.ok) throw new Error(response.status)
    var out = await response.json();
    setPlotInput(out);
    return response;
}

const UtilHeat = ({ menu, traceFolder }, url) => {
    const [plotInput, setPlotInput] = useState([]);

    useEffect(() => {
        if (traceFolder) {
            fetchData({ setPlotInput }, `http://localhost:5000/util_heat?folder=${traceFolder}`);
        }
    }, [traceFolder])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const CommHeat = ({ menu, traceFolder }, url) => {
    const [plotInput, setPlotInput] = useState([]);

    useEffect(() => {
        if (traceFolder) {
            fetchData({ setPlotInput }, `http://localhost:5000/comm_heat?folder=${traceFolder}`);
        }
    }, [traceFolder])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const MemHeat = ({ menu, traceFolder }) => {
    const [plotInput, setPlotInput] = useState([]);

    useEffect(() => {
        if (traceFolder) {
            fetchData({ setPlotInput }, `http://localhost:5000/mem_heat?folder=${traceFolder}`);
        }
    }, [traceFolder])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};


const UtilView = ({ menu, traceFolder }) => {
    return (
        <>
            <UtilHeat traceFolder={traceFolder} />
            <CommHeat traceFolder={traceFolder} />
            <MemHeat traceFolder={traceFolder} />
        </>
    );
};

export default UtilView;