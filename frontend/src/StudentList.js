import React, { useState, useEffect } from 'react';
import axios from './axiosInstance';
import { Link } from 'react-router-dom';

const StudentList = () => {
  const [students, setStudents] = useState([]);

  useEffect(() => {
    axios.get('/students/')
      .then(response => {
        setStudents(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the students!', error);
      });
  }, []);

  return (
    <div>
      <h2>Student List</h2>
      <ul>
        {students.map(student => (
          <li key={student.id}>
            {student.first_name} {student.last_name} - {student.email}
            <Link to={`/students/${student.id}/edit`}>Edit</Link>
            <Link to={`/students/${student.id}/delete`}>Delete</Link>
          </li>
        ))}
      </ul>
      <Link to="/students/new">Add Student</Link>
    </div>
  );
};

export default StudentList;
