import React, { useState } from 'react';
import axiosInstance from './axiosInstance';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });

    const { username, password } = formData;

    const onChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const onSubmit = async (e) => {
        e.preventDefault();
        const newUser = {
            username,
            password,
        };

        try {
            await axiosInstance.post('/register/', newUser);
            alert('User registered successfully');
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <form onSubmit={onSubmit}>
            <input
                type="text"
                name="username"
                value={username}
                onChange={onChange}
                placeholder="Username"
                required
            />
            <input
                type="password"
                name="password"
                value={password}
                onChange={onChange}
                placeholder="Password"
                required
            />
            <button type="submit">Register</button>
        </form>
    );
};

export default Register;
