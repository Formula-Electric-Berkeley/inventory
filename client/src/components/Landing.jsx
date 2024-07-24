import React, { useRef } from 'react';

const Landing = () => {
    return (
        <div className='w-full flex justify-center'>
            <div className='w-[1000px]'>
                <div className='w-full flex justify-between my-10'>
                    <div className='w-[250px] bg-gray-300 text-center box-shadow rounded-2xl py-7'>
                        <p className='text-3xl'>99 ITEMS</p>
                        <p className='text-base text-fuchsia-600'>OUT OF STOCK</p>
                    </div>
                    <div className='w-[250px] bg-gray-200 text-center box-shadow rounded-2xl py-7'>
                        <p className='text-3xl'>99 ITEMS</p>
                        <p className='text-base text-rose-600'>NOT PUT BACK</p>
                    </div>
                    <div className='w-[250px] bg-gray-100 text-center box-shadow rounded-2xl py-7'>
                        <p className='text-3xl'>99 ITEMS</p>
                        <p className='text-base text-blue-600'>LOW STOCK</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Landing;
