import './App.css'
import './index.css';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./components/Landing";

function App() {
    return (
        <BrowserRouter>
            <Routes basename="/inventory">
                <Route path="/" element={<Landing />}>
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
