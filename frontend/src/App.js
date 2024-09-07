import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Register from './Register';
import Login from './Login';
import CourseList from './CourseList';
import CourseForm from './CourseForm';
import CourseDelete from './CourseDelete';
import StudentList from './StudentList'; // Import StudentList component
import StudentForm from './StudentForm'; // Import StudentForm component
import StudentDelete from './StudentDelete'; // Import StudentDelete component
import './App.css';
import logo from './logo.svg';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <p>
            Edit <code>src/App.js</code> and save to reload.
          </p>
          <a
            className="App-link"
            href="https://reactjs.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            Learn React
          </a>
        </header>
        <Routes>
          <Route exact path="/register" element={<Register />} />
          <Route exact path="/login" element={<Login />} />
          <Route path="/courses" element={<CourseList />} />
          <Route path="/courses/new" element={<CourseForm />} />
          <Route path="/courses/:id/edit" element={<CourseForm />} />
          <Route path="/courses/:id/delete" element={<CourseDelete />} />
          <Route path="/students" element={<StudentList />} /> {/* Add StudentList route */}
          <Route path="/students/new" element={<StudentForm />} /> {/* Add StudentForm route */}
          <Route path="/students/:id/edit" element={<StudentForm />} /> {/* Add StudentForm route */}
          <Route path="/students/:id/delete" element={<StudentDelete />} /> {/* Add StudentDelete route */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
