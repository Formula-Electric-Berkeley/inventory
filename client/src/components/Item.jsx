import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { faArrowLeft, faBarcode, faMicrochip, faPen, faSave, faTrash, faCirclePlus, faCircleMinus } from '@fortawesome/free-solid-svg-icons'
import ReactToPrint from "react-to-print";
import ItemQrCode from "./QrCode";
import classnames from 'classnames';

const Item = () => {
    const { itemId } = useParams();

    const componentRef = useRef();

    const [itemData, setItemData] = useState({});
    const [error, setError] = useState(null);

    const [inEditMode, setInEditMode] = useState(false);

    useEffect(() => {
        const fetchParts = async () => {
            try {
                const response = await fetch(`${window.env.REACT_APP_API_URL}/api/item/get/${itemId}`);

                if (response.status === 404) {
                    throw new Error('Not Found')
                } else if (!response.ok) {
                    throw new Error('Network response failure');
                }

                const data = await response.json();
                setItemData(data.body[0]);
            } catch (error) {
                setError(error.message);
            }
        };

        fetchParts();
    }, [itemId]);

    const handleArrowOnClick = () => {
        window.location.href = '/'
    }

    const handleUpdateItemData = () => {
        const formdata = new FormData();

        formdata.append("api_key", "636e0c5c873afcef9a6fa5996edc9c8da49891b7b1ffbdb1720221ccf1e0e184");
        formdata.append("item_id", itemId)
        formdata.append("box_id", itemData.box_id)
        formdata.append("mfg_part_number", itemData.mfg_part_number)
        formdata.append("quantity", itemData.quantity)
        formdata.append("description", itemData.description)
        formdata.append("digikey_part_number", itemData.digikey_part_number)
        formdata.append("mouser_part_number", itemData.mouser_part_number)
        formdata.append("jlcpcb_part_number", itemData.jlcpcb_part_number)

        const requestOptions = {
            method: "POST",
            body: formdata,
        };

        fetch(`${window.env.REACT_APP_API_URL}/api/item/update`, requestOptions)
            .then((response) => {
                if (response.ok) {
                    alert("Item Updated Successfully!")
                }
            })
            .catch((error) => alert(error));

        setInEditMode(!inEditMode);
    }

    const handleDeleteItem = () => {
        if (confirm("Are you sure you want to delete this item?\nThis action cannot be undone.")) {
            const formdata = new FormData();
            formdata.append("item_id", itemId);
            formdata.append("api_key", "636e0c5c873afcef9a6fa5996edc9c8da49891b7b1ffbdb1720221ccf1e0e184");

            const requestOptions = {
                method: "POST",
                body: formdata,
                redirect: "follow"
            };

            fetch(`${window.env.REACT_APP_API_URL}/api/item/remove`, requestOptions)
                .then((response) => response.text())
                .then(() => window.location.href = '/')
                .catch((error) => alert(error));
        }
    }

    if (error === 'Not Found') {
        return (
            <div className='w-full flex justify-center mt-20'>
                <div>
                    <h1>Item not found!</h1>
                    <h1>Item ID: {itemId}</h1>
                </div>
            </div>
        )
    } else {
        return (
            <div className='flex justify-center'>
                <span onClick={handleArrowOnClick}>
                    <FontAwesomeIcon className="fixed top-4 left-4 size-10 cursor-pointer" icon={faArrowLeft} />
                </span>
                <span>
                    <FontAwesomeIcon className="fixed top-4 right-36 size-10 cursor-pointer hover:text-gray-500" onClick={() => { (inEditMode ? handleUpdateItemData() : setInEditMode(!inEditMode)) }} icon={inEditMode ? faSave : faPen} />
                </span>
                <ReactToPrint
                    trigger={() =>
                        <button>
                            <FontAwesomeIcon className="fixed top-4 right-20 size-10 cursor-pointer hover:text-gray-500 transition" icon={faBarcode} />
                        </button>}
                    content={() => componentRef.current}
                />
                <span onClick={handleDeleteItem}>
                    <FontAwesomeIcon className="fixed top-4 right-5 size-10 cursor-pointer hover:text-red-500 transition" icon={faTrash} />
                </span>
                <div className="text-center w-[1000px]">
                    <h1 className="text-4xl font-semibold my-10">{itemData.description}</h1>
                    <div className="hidden">
                        <div ref={componentRef}>
                            <ItemQrCode link={window.location.href} boxId={itemData.box_id}
                                mfgNum={itemData.mfg_part_number} desc={itemData.description} />
                        </div>
                    </div>
                    <div className="flex justify-center items-center m-auto w-60 h-60 border-2 border-black rounded-2xl">
                        <FontAwesomeIcon className="size-20" icon={faMicrochip} />
                    </div>
                    <div className="flex justify-between w-full mt-10">
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            {inEditMode ?
                                <input
                                    className="text-3xl font-bold w-full text-center"
                                    defaultValue={itemData.box_id}
                                    onChange={(e) =>
                                        setItemData(prevState => ({
                                            ...prevState,
                                            box_id: e.target.value
                                        }))
                                    }
                                />
                                :
                                <h1 className="text-3xl font-bold">{itemData.box_id}</h1>
                            }

                            <h1 className="text-xl">Box ID</h1>
                        </div>
                        <div className="w-64 py-5 border-2 border-black rounded-2xl flex flex-col">
                            <div className="w-full flex flex-row items-center justify-between text-center px-8">
                                <a onClick={() =>
                                    setItemData(prevState => ({
                                        ...prevState,
                                        quantity: String(Number(itemData.quantity) - 1)
                                    }))
                                }>
                                    <FontAwesomeIcon className={classnames(inEditMode ? "w-7 h-7 hover:cursor-pointer" : "w-0")} icon={faCircleMinus} />
                                </a>
                                {inEditMode ?
                                    <input
                                        className="text-3xl font-bold w-full text-center"
                                        value={itemData.quantity}
                                        defaultValue={itemData.quantity}
                                        onChange={(e) =>
                                            setItemData(prevState => ({
                                                ...prevState,
                                                quantity: e.target.value
                                            }))
                                        }
                                    />
                                    :
                                    <h1 className="text-3xl font-bold">{itemData.quantity}</h1>
                                }
                                <a onClick={() =>
                                    setItemData(prevState => ({
                                        ...prevState,
                                        quantity: String(Number(itemData.quantity) + 1)
                                    }))
                                }>
                                    <FontAwesomeIcon className={classnames(inEditMode ? "w-7 h-7 hover:cursor-pointer" : "w-0")} icon={faCirclePlus} />
                                </a>
                            </div>
                            <h1 className="text-xl">Quantity</h1>
                        </div>
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            {inEditMode ?
                                <input
                                    className="text-3xl font-bold w-full text-center"
                                    defaultValue={itemData.mfg_part_number}
                                    onChange={(e) =>
                                        setItemData(prevState => ({
                                            ...prevState,
                                            mfg_part_number: e.target.value
                                        }))
                                    }
                                />
                                :
                                <h1 className="text-3xl font-bold">{itemData.mfg_part_number}</h1>
                            }
                            <h1 className="text-xl">Manufacturer PN</h1>
                        </div>
                    </div>
                    <div className="flex justify-between w-full mt-10">
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            {inEditMode ?
                                <input
                                    className="text-3xl font-bold w-full text-center"
                                    defaultValue={itemData.digikey_part_number}
                                    onChange={(e) =>
                                        setItemData(prevState => ({
                                            ...prevState,
                                            digikey_part_number: e.target.value
                                        }))
                                    }
                                />
                                :
                                <h1 className="text-3xl font-bold">{itemData.digikey_part_number}</h1>
                            }
                            <h1 className="text-xl">DigiKey PN</h1>
                        </div>
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            {inEditMode ?
                                <input
                                    className="text-3xl font-bold w-full text-center"
                                    defaultValue={itemData.mouser_part_number}
                                    onChange={(e) =>
                                        setItemData(prevState => ({
                                            ...prevState,
                                            mouser_part_number: e.target.value
                                        }))
                                    }
                                />
                                :
                                <h1 className="text-3xl font-bold">{itemData.mouser_part_number}</h1>
                            }
                            <h1 className="text-xl">Mouser PN</h1>
                        </div>
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            {inEditMode ?
                                <input
                                    className="text-3xl font-bold w-full text-center"
                                    defaultValue={itemData.jlcpcb_part_number}
                                    onChange={(e) =>
                                        setItemData(prevState => ({
                                            ...prevState,
                                            jlcpcb_part_number: e.target.value
                                        }))
                                    }
                                />
                                :
                                <h1 className="text-3xl font-bold">{itemData.jlcpcb_part_number}</h1>
                            }
                            <h1 className="text-xl">JLCPCB PN</h1>
                        </div>
                    </div>
                </div>
            </div >
        );
    }
};

export default Item;
