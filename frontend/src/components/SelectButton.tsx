// @ts-nocheck
import { useState, useEffect } from 'react';

import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';

const SelectButton = ({ traceFolder, setTraceFolder }) => {

    const [folderOptions, setFolderOptions] = useState([]);

    const handleChange = (event) => {
      setTraceFolder(event.target.value);
    };

    const fetchData = async () => {

        const response = await fetch(`http://localhost:5000/traces`, {
            headers: { accept: "application/json" },
            method: "GET"
        })

        if (!response.ok) throw new Error(response.status)
        const out = await response.json();
        setFolderOptions(out.traces);
        return response;
    }


    useEffect(() => {
        if (folderOptions.length === 0) {
            console.log(folderOptions)
            console.log(traceFolder)
            fetchData()
        }
    }, [])

    return (
        <Box sx={{ minWidth: 120, mt: '24px' }}>
            {folderOptions.length > 0 &&
                <FormControl fullWidth>
                    <InputLabel id="demo-simple-select-label">Trace Folder</InputLabel>
                    <Select
                        labelId="demo-simple-select-label"
                        id="demo-simple-select"
                        value={traceFolder}
                        label="Trace Folder"
                        onChange={handleChange}
                    >
                        {folderOptions.map((folder, index) => (
                            <MenuItem key={index} value={folder}>{folder}</MenuItem>
                        ))}
                    </Select>
                </FormControl>
            }
      </Box>
    );
}
export default SelectButton;