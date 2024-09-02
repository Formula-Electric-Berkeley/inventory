import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

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
                console.log(data.body[0]);
                setItemData(data.body[0]);
            } catch (error) {
                setError(error.message);
            }
        };

        fetchParts();
    }, [itemId]);

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
            <div className='w-full flex justify-center mt-20'>
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
            </div>
        );
    }
};

export default Item;
