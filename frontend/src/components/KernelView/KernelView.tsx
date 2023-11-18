// @ts-nocheck
import "./KernelView.css"
import { useFetch, useAsync } from "react-async"
import { useState, useEffect } from 'react'
import { Layout } from 'antd';
import Plot from 'react-plotly.js';

function KernelView({ traceFolder }) {
    const [plotInput, setPlotInput] = useState({});

    const fetchData = async () => {
            
        const response = await fetch(`http://localhost:5000/kernel?folder=${traceFolder}`, {
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

    console.log('kernal render')

    useEffect(() => {
        //var {data, error} = useAsync({ promiseFn: fetchData, setPlotInput, rank })
        if (traceFolder) {
            console.log('fetching kernal data')
            fetchData()
        }
    }, [traceFolder]);

    return (
        <>
            <Layout>
                <Layout.Content className="innercontent">
                    <Plot data={plotInput.data} layout={plotInput.layout} />
                </Layout.Content>
            </Layout>
        </>
    );
}

export default KernelView;
