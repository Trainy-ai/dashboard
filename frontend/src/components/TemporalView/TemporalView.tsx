// @ts-nocheck
import "./TemporalView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js';

const TemporalView = ({ menu, traceFolder }) => {
    const [plotInput, setPlotInput] = useState([]);

    const fetchData = async () => {

        const response = await fetch(`http://localhost:5000/temporal?folder=${traceFolder}`, {
            headers: { accept: "application/json" },
            method: "GET"
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
        if (traceFolder) {
            fetchData()
        }
    }, [traceFolder])

    return (
        <>
            <Plot data={plotInput.data} layout={plotInput.layout} />
        </>
    );
};

export default TemporalView;
