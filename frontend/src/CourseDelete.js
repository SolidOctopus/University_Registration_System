import React from 'react';
import axios from './axiosInstance'; // Adjust the path to your Axios instance
import { useNavigate, useParams } from 'react-router-dom';

const CourseDelete = () => {
    const { id } = useParams();
    const navigate = useNavigate();

    const handleDelete = () => {
        axios.delete(`/courses/${id}/delete/`)
            .then(() => {
                navigate('/courses');
            })
            .catch(error => {
                console.error('There was an error deleting the course!', error);
            });
    };

    return (
        <div>
            <h2>Are you sure you want to delete this course?</h2>
            <button onClick={handleDelete}>Yes, delete</button>
            <button onClick={() => navigate('/courses')}>Cancel</button>
        </div>
    );
};

export default CourseDelete;
