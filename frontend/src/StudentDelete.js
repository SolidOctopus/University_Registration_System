import React from 'react';
import axios from './axiosInstance';
import { useNavigate, useParams } from 'react-router-dom';

const StudentDelete = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const handleDelete = () => {
    axios.delete(`/students/${id}/`)
      .then(() => {
        navigate('/students');
      })
      .catch(error => {
        console.error('There was an error deleting the student!', error);
      });
  };

  return (
    <div>
      <h2>Are you sure you want to delete this student?</h2>
      <button onClick={handleDelete}>Yes, delete</button>
      <button onClick={() => navigate('/students')}>Cancel</button>
    </div>
  );
};

export default StudentDelete;
