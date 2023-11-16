// @ts-nocheck
import "./TemporalView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js';

const fetchData = async ({ setPlotInput }) => {
    const response = await fetch(`http://localhost:5000/temporal_dev`, {
        headers: { accept: "application/json" },
    })
    if (!response.ok) throw new Error(response.status)
    var out = await response.json();
    setPlotInput([out]);
    //console.log('inside');
    //console.log(response);
    //console.log(out);
    //console.log(out['idle_time_pctg']);
    return response;
}

const TemporalView = ({ menu }) => {
    const [plotInput, setPlotInput] = useState([]);

    const fetchData = async ({ setPlotInput }) => {
        const response = await fetch(`http://localhost:5000/temporal`, {
            headers: { accept: "application/json" },
        })

        if (!response.ok) throw new Error(response.status)
        var out = await response.json();
        setPlotInput(out);
        //console.log('inside');
        //console.log(response);
        //console.log(out);
        //console.log(out['idle_time_pctg']);
        return response;
    }

    //var {data, error} = useAsync({ promiseFn: fetchData, setPlotInput, rank })

    useEffect(() => {
        fetchData({ setPlotInput })
    }, [])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

export default TemporalView;
