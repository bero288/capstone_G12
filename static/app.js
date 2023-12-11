//accesing the inputs in the form
const form = document.querySelector("form");
const percentBiking = document.querySelector("#percent-biking");
const percentSmoking = document.querySelector("#percent-smoking");
//saving data to local storage
function saveToLocalStorage(event) {
  //preventing the form from reloading the page
  event.preventDefault();
  localStorage.setItem("name", "Ebraam");
  localStorage.setItem("percentSmoking", percentSmoking.value);
  postTheData();
  form.reset();
}
//redirecting to the page of prediction
function redirecting() {
  window.location.replace("/predict");
}
//sending the data to the backend server to use them in the AI model
function postTheData() {
  fetch("/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json; charset=UTF-8",
    },
    body: JSON.stringify({
      percentSmoking: localStorage.getItem("percentSmoking"),
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Handle the response from the Flask server
      for (let key in data) {
        console.log(key);
        console.log(data[key]);
      }
    })
    .catch((error) => {
      // Handle any error that occurs during the request
      console.error("Error:", error);
    });
}

/*fetch("/google-fit-data", {
  method: "GET",
  headers: {
    Authorization: "https://oauth2.googleapis.com/token",
    "Content-Type": "application/json",
  },
})
  .then((response) => response.json())
  .then((data) => {
    // Handle the response from the Flask server
    console.log(data);
  })
  .catch((error) => {
    // Handle any error that occurs during the request
    console.error("Error:", error);
  });*/

fetch("https://www.googleapis.com/fitness/v1/users/me/dataSources", {
  method: "GET",
  headers: {
    Authorization: "https://oauth2.googleapis.com/token",
    "Content-Type": "application/json",
  },
})
  .then((response) => response.json())
  .then((data) => {
    // Handle the response from the Flask server
    console.log(data);
  })
  .catch((error) => {
    // Handle any error that occurs during the request
    console.error("Error:", error);
  });
