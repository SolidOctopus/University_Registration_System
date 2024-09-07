import React, { useState, useEffect } from 'react';
import axios from './axiosInstance';
import { useNavigate, useParams } from 'react-router-dom';

const StudentForm = () => {
  const [first_name, setFirstName] = useState('');
  const [last_name, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const navigate = useNavigate();
  const { id } = useParams();

  useEffect(() => {
    if (id) {
      axios.get(`/students/${id}/`)
        .then(response => {
          const { first_name, last_name, email } = response.data;
          setFirstName(first_name);
          setLastName(last_name);
          setEmail(email);
        })
        .catch(error => {
          console.error('There was an error fetching the student!', error);
        });
    }
  }, [id]);

  const handleSubmit = (event) => {
    event.preventDefault();

    const student = { first_name, last_name, email };

    if (id) {
      axios.put(`/students/${id}/`, student)
        .then(() => {
          navigate('/students');
        })
        .catch(error => {
          console.error('There was an error updating the student!', error);
        });
    } else {
      axios.post('/students/', student)
        .then(() => {
          navigate('/students');
        })
        .catch(error => {
          console.error('There was an error creating the student!', error);
        });
    }
  };

  return (
    <div>
      <h2>{id ? 'Edit' : 'Add'} Student</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>First Name</label>
          <input
            type="text"
            value={first_name}
            onChange={(e) => setFirstName(e.target.value)}
          />
        </div>
        <div>
          <label>Last Name</label>
          <input
            type="text"
            value={last_name}
            onChange={(e) => setLastName(e.target.value)}
          />
        </div>
        <div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <button type="submit">Save</button>
      </form>
    </div>
  );
};

export default StudentForm;
