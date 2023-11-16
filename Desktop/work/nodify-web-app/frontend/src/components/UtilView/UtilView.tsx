// @ts-nocheck
import "./UtilView.css";
import { useState, useEffect } from 'react';
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

const UtilHeat = ({ menu }, url) => {
    const [plotInput, setPlotInput] = useState([]);

    useEffect(() => {
        fetchData({ setPlotInput }, `http://localhost:5000/util_heat`);
    }, [])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const CommHeat = ({ menu }, url) => {
    const [plotInput, setPlotInput] = useState([]);

    useEffect(() => {
        fetchData({ setPlotInput }, `http://localhost:5000/comm_heat`);
    }, [])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

const MemHeat = ({ menu }, url) => {
    const [plotInput, setPlotInput] = useState([]);

    useEffect(() => {
        fetchData({ setPlotInput }, `http://localhost:5000/mem_heat`);
    }, [])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};


const UtilView = ({ menu }) => {
    return (
        <>
            <UtilHeat />
            <CommHeat />
            <MemHeat />
        </>
    );
};

export default UtilView;