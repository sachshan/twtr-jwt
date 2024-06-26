import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ScrollView, StyleSheet, ActivityIndicator } from "react-native";
import TweetList from "./TweetList";
import { Map, Marker } from "pigeon-maps";

const THome = () => {
  const [tweets, setTweets] = useState([]);
  const [loading, setLoading] = useState(true);   
  const [locations, setLocations] = useState([]);

  // save keys to local storage
  const localStorageAuthKey = 'twtr:auth';
  function saveAuthorisation(keys) {
    if (typeof Storage !== 'undefined') {
      try {
        localStorage.setItem(localStorageAuthKey, JSON.stringify(keys));
      } catch (ex) {
        console.log(ex);
      }
    } else {
      // No web storage Support :-(
    }
  }

  function getAuthorisation() {
    if (typeof Storage !== 'undefined') {
      try {
        var keys = JSON.parse(localStorage.getItem(localStorageAuthKey));
        return keys.groupKey;
      } catch (ex) {
        console.log(ex);
      }
    } else {
      // No web storage Support :-(
    }
  }  

  const pollingRef = useRef(); // A "ref" tracks a value like state, but doesn't trigger a rerender

  const pollLocations = useCallback(() => {
    console.log("just polled");
    //poll for group locations
    const config = {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    }

    const groupkey = getAuthorisation();
    console.log("Signin.js: fetching from " + `${process.env.REACT_APP_API_SERVICE_URL}/map/${groupkey}`)
    // verify user/pwd, get encoded userid as access and refresh tokens in return
    // fetch(`http://localhost:5004/v1/map/${groupkey}`, config)
    // fetch(`${process.env.REACT_APP_BE_NETWORK}:${process.env.REACT_APP_BE_PORT}/map/user`, config)
    // fetch(`login`, config)
    fetch(`${process.env.REACT_APP_API_SERVICE_URL}/map/${groupkey}`, config)
      .then(response => response.json())
      .then(data => {
        // update Location Array with all the locations with their Names
        // console.dir(data);
        setLocations(data);
      })
      .catch((err) => {
        alert(err);
        console.log(err);
      });

      //send device location
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
           

          });
        }
        else {
          console.log("Geolocation is not supported by this browser.");
        };

    pollingRef.current = setTimeout(pollLocations, 4000);   
  }, []);

  useEffect(() => {
    const config = {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      }
    }

    const groupkey = getAuthorisation();
    console.log("Signin.js: fetching from " + `${process.env.REACT_APP_API_SERVICE_URL}/map/user`)
    // verify user/pwd, get encoded userid as access and refresh tokens in return
    // fetch(`http://localhost:5004/v1/map/${groupkey}`, config)
    fetch(`${process.env.REACT_APP_API_SERVICE_URL}/map/${groupkey}`, config)
    // fetch(`login`, config)
      .then(response => response.json())
      .then(data => {
        // update Location Array with all the locations with their Names
        // console.dir(data);
        setLocations(data);
      })
      .catch((err) => {
        alert(err);
        console.log(err);
      });

    pollingRef.current = setTimeout(pollLocations, 4000);
    return () => {
      // Clear the timeout when the component unmounts
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
      }
    };
  }, [pollingRef, pollLocations]);

  return (
    <div className='mainBody'>
      {/* Map Structure */}
      <Map height={500} defaultCenter={[42.338655864160486, -71.08808567486311]} defaultZoom={18}>
        {locations.map((point, i) => (
          <Marker key={i} width={50} anchor={point.location}>
            <div className='mapPoint'>
              {point.user_name}
            </div>
          </Marker>
        ))}
      </Map>

      {/* Users Structure */}
      <ScrollView noSpacer={true} noScroll={true} style={styles.container}>
      <ul>
        <h2>Memebers present</h2>
      {locations.map((point, i) => (
              <li>{point.user_name}</li>
          
        ))}
      </ul>
      </ScrollView>
     
    </div>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: "whitesmoke",
    marginTop: '60px'
  },
  centering: {
    alignItems: "center",
    justifyContent: "center",
    padding: 8,
    height: "100vh"
  },
});

// Add CSS styles for the mapPoint div
const mapPointStyles = `
  .mapPoint {
    background-color: red;
    color: white;
    padding: 2px 5px;
    border-radius: 5px;
    text-align: center;
    font-size: 12px;
    position: relative;
    transform: translate(-50%, -50%);
    white-space: nowrap;
  }

  .mapPoint::after {
    content: '';
    position: absolute;
    bottom: -5px; /* Adjust this to move the point */
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid red; /* Same as background color */
  }
`;

const styleSheet = document.createElement("style");
styleSheet.type = "text/css";
styleSheet.innerText = mapPointStyles;
document.head.appendChild(styleSheet);

export default THome;
