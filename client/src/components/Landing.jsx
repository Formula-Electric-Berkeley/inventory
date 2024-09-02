import Table from "./Table";

const Landing = () => {
    return (
        <div className='w-full flex justify-center'>
            <div className='w-[1000px]'>
                <div className='w-full flex justify-between my-10'>
                    <div className='w-[275px] bg-white text-center box-shadow rounded-2xl py-5'>
                        <p className='text-3xl'>99 ITEMS</p>
                        <p className='text-base text-fuchsia-600'>OUT OF STOCK</p>
                    </div>
                    <div className='w-[275px] bg-white text-center box-shadow rounded-2xl py-5'>
                        <p className='text-3xl'>99 ITEMS</p>
                        <p className='text-base text-rose-600'>NOT PUT BACK</p>
                    </div>
                    <div className='w-[275px] bg-white text-center box-shadow rounded-2xl py-5'>
                        <p className='text-3xl'>99 ITEMS</p>
                        <p className='text-base text-blue-600'>LOW STOCK</p>
                    </div>
                </div>
                <Table />
            </div>
        </div>
    );
};

export default Landing;
