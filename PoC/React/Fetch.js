import axios from 'axios';
import React, { useState, useEffect } from 'react';
import './Card.css';


function Fetch() {
    const [posts, setPosts] = useState([])
    useEffect(() => {
        
        axios.get('https://kg3afcrwig.execute-api.eu-central-1.amazonaws.com/PoC/db_crawling?')
            .then(res => {
                console.log(res)
                setPosts(res.data)
            })
            .catch(err => {
                console.log(err)
            })
    })
    return (
        <div className="results">
            {posts.map((post) => (
                <div className="card">
                    <div className="immagine">
                      <img src={'https://dream-team-instagram-images.s3.eu-central-1.amazonaws.com/' + post.image_s3} className={post.image_s3 == "null" ? 'hidden' : 'card_image'} alt=" "/>
                    </div>
                    <div className="info">
                        <h2 className={post.location == "null" ? 'hidden' : 'card_location'}>{post.location}</h2>
                        <p className={post.testo_post == "null" ? 'hidden' : 'card_post'}><span className="titoletto">Post social: </span>{post.testo_post}</p>
                        <p className={post.id_utente == "null" ? 'hidden' : 'card_username'}><span className="titoletto">Utente:</span> {post.id_utente}</p>
                        <p className={post.latitudine == "null" ? 'hidden' : 'card_latitude'}><span className="titoletto">Latitudine:</span> {post.latitudine}</p>
                        <p className={post.longitudine == "null" ? 'hidden' : 'card_longitude'}><span className="titoletto">Longitudine:</span> {post.longitudine}</p>
                        <p className={post.phone == "null" ? 'hidden' : 'card_phone'}><span className="titoletto">Numero di telefono:</span> {post.phone}</p>
                    </div>
                    <div className="result">
                        <p className={post.sentiment == "null" ? 'hidden' : 'card_comprehend'}><span className="titoletto">Comprehend: </span> {post.sentiment}</p>
                        <p className={post.tag_rekognition == "null" ? 'hidden' : 'card_rekognition'}><span className="titoletto">Rekognition:</span> {post.tag_rekognition}</p>
                        <p className={post.emotion_rekognition == "null" ? 'hidden' : 'card_rekognition'}><span className="titoletto">Emotion Rekognition:</span> {post.emotion_rekognition}</p>
                        <p className={post.category == "null" ? 'hidden' : 'card_category'}><span className="titoletto">Categoria:</span> {post.category}</p>
                        <a className={post.web_site == "null" ? 'hidden' : 'card_website'} href={post.web_site} target="_blank">Vai al sito</a>
                    </div>

                </div>
            ))}
        </div>)
}
export default Fetch;
