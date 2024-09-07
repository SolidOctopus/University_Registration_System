import React, { useState, useEffect } from 'react';
import axios from './axiosInstance'; // Adjust the path to your Axios instance
import { useNavigate, useParams } from 'react-router-dom';

const CourseForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        schedule: '',
        capacity: '',
    });
    const { id } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        if (id) {
            axios.get(`/courses/${id}/edit/`)
                .then(response => {
                    setFormData(response.data);
                })
                .catch(error => {
                    console.error('There was an error fetching the course!', error);
                });
        }
    }, [id]);

    const handleChange = e => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = e => {
        e.preventDefault();
        if (id) {
            axios.put(`/courses/${id}/edit/`, formData)
                .then(() => {
                    navigate('/courses');
                })
                .catch(error => {
                    console.error('There was an error updating the course!', error);
                });
        } else {
            axios.post('/courses/new/', formData)
                .then(() => {
                    navigate('/courses');
                })
                .catch(error => {
                    console.error('There was an error creating the course!', error);
                });
        }
    };

    return (
        <div>
            <h2>{id ? 'Edit Course' : 'Add Course'}</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Course Name"
                    required
                />
                <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    placeholder="Course Description"
                    required
                />
                <input
                    type="text"
                    name="schedule"
                    value={formData.schedule}
                    onChange={handleChange}
                    placeholder="Course Schedule"
                    required
                />
                <input
                    type="number"
                    name="capacity"
                    value={formData.capacity}
                    onChange={handleChange}
                    placeholder="Course Capacity"
                    required
                />
                <button type="submit">{id ? 'Update' : 'Add'}</button>
            </form>
        </div>
    );
};

export default CourseForm;
