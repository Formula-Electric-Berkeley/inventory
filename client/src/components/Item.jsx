import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { faArrowLeft, faMicrochip } from '@fortawesome/free-solid-svg-icons'

const Item = () => {
    const { itemId } = useParams();

    const [itemData, setItemData] = useState({});
    const [error, setError] = useState(null);

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
                <div className="text-center w-[1000px]">
                    <h1 className="text-4xl font-semibold my-10">{itemData.description}</h1>
                    <div className="flex justify-center items-center m-auto w-60 h-60 border-2 border-black rounded-2xl">
                        <FontAwesomeIcon className="size-20" icon={faMicrochip} />
                    </div>
                    <div className="flex justify-between w-full mt-10">
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            <h1 className="text-3xl font-bold">{itemData.box_id}</h1>
                            <h1 className="text-xl">Box ID</h1>
                        </div>
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            <h1 className="text-3xl font-bold">{itemData.quantity}</h1>
                            <h1 className="text-xl">Quantity</h1>
                        </div>
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            <h1 className="text-3xl font-bold">{itemData.mfg_part_number}</h1>
                            <h1 className="text-xl">Manufacturer PN</h1>
                        </div>
                    </div>
                    <div className="flex justify-between w-full mt-10">
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            <h1 className="text-3xl font-bold">{itemData.digikey_part_number}</h1>
                            <h1 className="text-xl">DigiKey PN</h1>
                        </div>
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            <h1 className="text-3xl font-bold">{itemData.mouser_part_number}</h1>
                            <h1 className="text-xl">Mouser PN</h1>
                        </div>
                        <div className="w-64 py-5 border-2 border-black rounded-2xl">
                            <h1 className="text-3xl font-bold">{itemData.jlcpcb_part_number}</h1>
                            <h1 className="text-xl">JLCPCB PN</h1>
                        </div>
                    </div>
                </div>
                {/*
                <div>
                    <h1>Box Id: {itemData.box_id}</h1>
                    <h1>Created By: {itemData.created_by}</h1>
                    <h1>Created Epoch Millis: {itemData.created_epoch_millis}</h1>
                    <h1>Description: {itemData.description}</h1>
                    <h1>DigiKey Part Number: {itemData.digikey_part_number}</h1>
                    <h1>Item Id: {itemData.item_id}</h1>
                    <h1>JLCPCB: {itemData.jlcpcb_part_number}</h1>
                    <h1>Manufacturer Part Number: {itemData.mfg_part_number}</h1>
                    <h1>Mouser Part Number: {itemData.mouser_part_number}</h1>
                    <h1>Quantity: {itemData.quantity}</h1>
                </div>
            */}
            </div>
        );
    }
};

export default Item;
