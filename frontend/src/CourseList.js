import React, { useState, useEffect } from 'react';
import axios from './axiosInstance'; // Adjust the path to your Axios instance

const CourseList = () => {
    const [courses, setCourses] = useState([]);

    useEffect(() => {
        axios.get('/courses/')
            .then(response => {
                setCourses(response.data);
            })
            .catch(error => {
                console.error('There was an error fetching the courses!', error);
            });
    }, []);

    return (
        <div>
            <h2>Course List</h2>
            <a href="/courses/new">Add New Course</a>
            <ul>
                {courses.map(course => (
                    <li key={course.id}>
                        {course.name} - {course.description} - {course.schedule} - {course.capacity} seats
                        <a href={`/courses/${course.id}/edit`}>Edit</a>
                        <a href={`/courses/${course.id}/delete`}>Delete</a>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default CourseList;

