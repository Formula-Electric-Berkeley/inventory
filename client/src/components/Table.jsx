import { useState, useCallback, useEffect } from 'react';
import { AgGridReact } from 'ag-grid-react';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";

const Table = () => {
    const [colDefs] = useState([
        { headerName: "Description", field: "description", flex: 1 },
        { headerName: "Box ID", field: "box_id", flex: 0.7 },
        { headerName: "Quantity", field: "quantity", flex: 0.5 },
        { headerName: "Manufacturer Part Number", field: "mfg_part_number", flex: 1 },
        { headerName: "DigiKey Part Number", field: "digikey_part_number", flex: 1 },
        { headerName: "JLCPCB Part Number", field: "jlcpcb_part_number", flex: 1 },
        { headerName: "Mouser Part Number", field: "mouser_part_number", flex: 1 },
    ]);

    const [rowData, setRowData] = useState([]);

    useEffect(() => {
        const fetchParts = async () => {
            try {
                const response = await fetch(`${window.env.REACT_APP_API_URL}/api/items/list`);

                if (!response.ok) {
                    throw new Error('Network response failure');
                }

                const data = await response.json();
                setRowData(data.body);
            } catch (error) {
                console.error(error.message);
            }
        };

        fetchParts();
    }, []);

    const [quickFilterText, setQuickFilterText] = useState();
    const onFilterTextBoxChanged = useCallback(
        ({ target: { value } }) =>
            setQuickFilterText(value),
        []
    );

    return (
        <div>
            <input
                type="text"
                id="filter-text-box"
                placeholder="Search Inventory..."
                onInput={onFilterTextBoxChanged}
                className='w-full box-shadow text-center py-2 rounded-full mb-7'
            />
            <div
                className="ag-theme-quartz w-full h-[60vh]"
            >
                <AgGridReact
                    className='w-full'
                    rowData={rowData}
                    columnDefs={colDefs}
                    quickFilterText={quickFilterText}
                />
            </div>
            <div className='w-100 flex justify-end mt-2'>
                <p>
                    # of Items: {rowData.length}
                </p>
            </div>
        </div>
    );
};

export default Table;
