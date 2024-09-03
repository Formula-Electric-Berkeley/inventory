import Table from "./Table";

const Landing = () => {
    return (
        <div className='w-full flex justify-center'>
            <div className='w-[1000px]'>
                <div className='w-full text-center my-10'>
                    <h1 className="text-4xl font-bold">Inventory Management System</h1>
                    <h2 className="text-xl mt-2">Created by Formula Electric at Berkeley</h2>
                </div>
                <Table />
            </div>
        </div>
    );
};

export default Landing;
