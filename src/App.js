import React, { Component } from 'react';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="root">
        <iframe className="view" />
        <div className="tools">
        </div>
      </div>
    );
  }
}

export default App;
