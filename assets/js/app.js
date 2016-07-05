var React = require('react');
var ReactDOM = require('react-dom')
import {Row, Col, Button} from "elemental"
const App = ()=> (
    <Row>
        <Col sm="1/5">
            <ul>
                <li>
                    学籍
                </li>
                <li>
                    成绩
                </li>
            </ul>
        </Col>
        <Col sm="4/5"><h1>Hello World</h1> </Col>
    </Row>
);

export default App
