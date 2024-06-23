import React, { useState, useEffect,useRef, useCallback  } from 'react';
import { ScrollView, StyleSheet, ActivityIndicator } from "react-native";
import TweetList from "./TweetList";
import { Map, Marker, Overlay } from "pigeon-maps"
//import axios from 'axios';

const THome = () => {
  const [tweets, setTweets] = React.useState([]);
  const [loading, setLoading] = React.useState(true);   
  
  const [locations, setLocations] = useState([[42.338655864160486, -71.08808567486311],
    [42.338525, -71.088320]]);

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
        console.dir(keys.groupKey);
        return keys.groupKey;

      } catch (ex) {
          console.log(ex);
      }
  } else {
      // No web storage Support :-(
  }
}  

  // useEffect(() => {
  //   const fetchData = async () => {
  //     //const res = await fetch("http://localhost:5000/tweets-results");
  //     // const res = await fetch(`${process.env.REACT_APP_BE_NETWORK}:${process.env.REACT_APP_BE_PORT}/tweets-results`);
  //     const res = await fetch(`/tweets-results`);
  //     // const res = await fetch(`tweets-results`);
  //     const { results } = await res.json();
  //     console.log(results);
  //     setTweets([...results]);
	//     setLoading(false);
  //   };
 
  //   console.log("Home.js: fetching from " + `${process.env.REACT_APP_API_SERVICE_URL}/tweets-results`)
  //   fetchData();
  // }, []);

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
      console.log("Signin.js: fetching from " + `${process.env.REACT_APP_API_SERVICE_URL}/map/user`)
      // verify user/pwd, get encoded userid as access and refresh tokens in return
      fetch(`http://localhost:5004/v1/map/${groupkey}`, config)
      // fetch(`${process.env.REACT_APP_BE_NETWORK}:${process.env.REACT_APP_BE_PORT}/map/user`, config)
      // fetch(`login`, config)
        .then(response => response.json())
        .then(data => {
          // update Location Array with all the locations with their Names
          // setLocations(data);
        
        })
        .catch( (err) => {
          alert(err);
          console.log(err);
        });
      
      setLocations([[42.339655864160486, -71.08808567486311],
        [42.338525, -71.088320]]);
      pollingRef.current = setTimeout(pollLocations,3000);   
    },[]);

    useEffect (
      () => {
        pollingRef.current = setTimeout(pollLocations,3000);
        return () => {
          // Clear the timeout when the component unmounts
          if (pollingRef.current) {
            clearTimeout(pollingRef.current);
          }
        };
      }, [pollingRef]
    );


  return (
    <div className='mainBody'>
{/* Map Structure */}


<Map height={300} defaultCenter={[42.338655864160486, -71.08808567486311]} defaultZoom={18}>
      {locations.map ((point, i) => (
          <Overlay width={50} anchor={point} >
            bob
          </Overlay>
      ))}
    </Map>

{/* Users Structure */}
    <ScrollView noSpacer={true} noScroll={true} style={styles.container}>
	  {loading ? (
	    <ActivityIndicator
		  style={[styles.centering]}
		  color="#ff8179"
		  size="large"
	    />
	  ) : (
	    <TweetList tweets={tweets} />
	  )}
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

export default THome;
