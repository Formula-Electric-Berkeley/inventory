import { useState, useCallback } from 'react';
import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component
import "ag-grid-community/styles/ag-grid.css"; // Mandatory CSS required by the Data Grid
import "ag-grid-community/styles/ag-theme-quartz.css"; // Optional Theme applied to the Data Grid


const Table = () => {
    const [colDefs, setColDefs] = useState([
        { field: "partNumber", flex: 1 },
        { field: "quantity", flex: 0.6 },
        { field: "location", flex: 1 },
        { field: "description", flex: 2 },
        { field: "lastUsed", flex: 1.5 }
    ]);

    const [rowData, setRowData] = useState([
        { partNumber: "87654321", quantity: 15, location: "EECS Box S0002", description: "High-quality resistor", lastUsed: "July 24, 2024 10:20 AM" },
        { partNumber: "12348765", quantity: 8, location: "EECS Box S0003", description: "Durable capacitor", lastUsed: "July 24, 2024 9:30 AM" },
        { partNumber: "98765432", quantity: 20, location: "EECS Box S0004", description: "Efficient diode", lastUsed: "July 24, 2024 8:45 AM" },
        { partNumber: "23456789", quantity: 12, location: "EECS Box S0005", description: "Reliable transistor", lastUsed: "July 24, 2024 11:00 AM" },
        { partNumber: "34567890", quantity: 5, location: "EECS Box S0006", description: "High-performance IC", lastUsed: "July 24, 2024 10:10 AM" },
        { partNumber: "45678901", quantity: 30, location: "EECS Box S0007", description: "Advanced microcontroller", lastUsed: "July 24, 2024 9:15 AM" },
        { partNumber: "56789012", quantity: 18, location: "EECS Box S0008", description: "Precise sensor", lastUsed: "July 24, 2024 11:30 AM" },
        { partNumber: "67890123", quantity: 25, location: "EECS Box S0009", description: "Robust motor", lastUsed: "July 24, 2024 10:40 AM" },
        { partNumber: "78901234", quantity: 10, location: "EECS Box S0010", description: "Flexible cable", lastUsed: "July 24, 2024 9:50 AM" },
        { partNumber: "89012345", quantity: 22, location: "EECS Box S0011", description: "Versatile connector", lastUsed: "July 24, 2024 8:30 AM" },
        { partNumber: "90123456", quantity: 17, location: "EECS Box S0012", description: "Compact battery", lastUsed: "July 24, 2024 11:15 AM" },
        { partNumber: "01234567", quantity: 28, location: "EECS Box S0013", description: "Durable switch", lastUsed: "July 24, 2024 10:25 AM" },
        { partNumber: "12345678", quantity: 14, location: "EECS Box S0014", description: "Efficient LED", lastUsed: "July 24, 2024 9:35 AM" },
        { partNumber: "23456780", quantity: 19, location: "EECS Box S0015", description: "Sensitive microphone", lastUsed: "July 24, 2024 8:50 AM" },
        { partNumber: "34567891", quantity: 9, location: "EECS Box S0016", description: "High-fidelity speaker", lastUsed: "July 24, 2024 11:05 AM" },
        { partNumber: "45678902", quantity: 13, location: "EECS Box S0017", description: "Powerful amplifier", lastUsed: "July 24, 2024 10:05 AM" },
        { partNumber: "56789013", quantity: 24, location: "EECS Box S0018", description: "Reliable power supply", lastUsed: "July 24, 2024 9:20 AM" },
        { partNumber: "67890124", quantity: 16, location: "EECS Box S0019", description: "Efficient transformer", lastUsed: "July 24, 2024 8:40 AM" },
        { partNumber: "78901235", quantity: 21, location: "EECS Box S0020", description: "Precise oscillator", lastUsed: "July 24, 2024 11:20 AM" },
        { partNumber: "89012346", quantity: 7, location: "EECS Box S0021", description: "Versatile potentiometer", lastUsed: "July 24, 2024 10:35 AM" },
        { partNumber: "54321098", quantity: 20, location: "EECS Box S0022", description: "High-voltage capacitor", lastUsed: "July 24, 2024 8:50 AM" },
        { partNumber: "65432109", quantity: 10, location: "EECS Box S0023", description: "Low-noise resistor", lastUsed: "July 24, 2024 9:05 AM" },
        { partNumber: "76543210", quantity: 15, location: "EECS Box S0024", description: "Thermistor for temperature sensing", lastUsed: "July 24, 2024 10:20 AM" },
        { partNumber: "87654321", quantity: 25, location: "EECS Box S0025", description: "Inductor for power circuits", lastUsed: "July 24, 2024 11:40 AM" },
        { partNumber: "98765432", quantity: 30, location: "EECS Box S0026", description: "Zener diode for voltage regulation", lastUsed: "July 24, 2024 12:10 PM" },
        { partNumber: "09876543", quantity: 40, location: "EECS Box S0027", description: "MOSFET transistor", lastUsed: "July 24, 2024 1:15 PM" },
        { partNumber: "10987654", quantity: 50, location: "EECS Box S0028", description: "NPN transistor", lastUsed: "July 24, 2024 2:25 PM" },
        { partNumber: "21098765", quantity: 35, location: "EECS Box S0029", description: "PNP transistor", lastUsed: "July 24, 2024 3:30 PM" },
        { partNumber: "32109876", quantity: 45, location: "EECS Box S0030", description: "Schottky diode", lastUsed: "July 24, 2024 4:10 PM" },
        { partNumber: "43210987", quantity: 60, location: "EECS Box S0031", description: "Ferrite bead", lastUsed: "July 24, 2024 5:00 PM" },
        { partNumber: "54321098", quantity: 18, location: "EECS Box S0032", description: "Ceramic capacitor", lastUsed: "July 24, 2024 5:50 PM" },
        { partNumber: "65432109", quantity: 22, location: "EECS Box S0033", description: "Electrolytic capacitor", lastUsed: "July 24, 2024 6:10 PM" },
        { partNumber: "76543210", quantity: 33, location: "EECS Box S0034", description: "Tantalum capacitor", lastUsed: "July 24, 2024 6:45 PM" },
        { partNumber: "87654321", quantity: 27, location: "EECS Box S0035", description: "Polymer capacitor", lastUsed: "July 24, 2024 7:30 PM" },
        { partNumber: "98765432", quantity: 32, location: "EECS Box S0036", description: "Multi-layer ceramic capacitor", lastUsed: "July 24, 2024 8:10 PM" },
        { partNumber: "09876543", quantity: 14, location: "EECS Box S0037", description: "Electret microphone", lastUsed: "July 24, 2024 8:50 PM" },
        { partNumber: "10987654", quantity: 29, location: "EECS Box S0038", description: "Surface mount LED", lastUsed: "July 24, 2024 9:15 PM" },
        { partNumber: "21098765", quantity: 11, location: "EECS Box S0039", description: "Through hole LED", lastUsed: "July 24, 2024 9:50 PM" },
        { partNumber: "32109876", quantity: 17, location: "EECS Box S0040", description: "Phototransistor", lastUsed: "July 24, 2024 10:20 PM" },
        { partNumber: "43210987", quantity: 21, location: "EECS Box S0041", description: "Triac for power control", lastUsed: "July 24, 2024 10:50 PM" }
    ]);

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
