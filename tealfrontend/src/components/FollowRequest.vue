<template>
    <div>
      <h1>Follow Requests</h1>
      <div v-if="followRequests.length">
        <div v-for="request in followRequests" :key="request.uuid">
          <p>{{ request.actor.displayName }} wants to follow you.</p>
          <button @click="acceptRequest(request.actor.uuid)">Accept</button>
          <button @click="declineRequest(request.actor.uuid)">Decline</button>
        </div>
      </div>
      <div v-else>
        <p>No follow requests.</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from '../axios';
  
  export default {
    props: ['uuid'],
    data() {
      return {
        followRequests: [],
      };
    },
    created() {
      this.fetchFollowRequests();
    },
    methods: {
      fetchFollowRequests() {
        const userUUID = localStorage.getItem('uuid');
        axios
          .get(`/authors/${userUUID}/follow_requests/`)
          .then((response) => {
            this.followRequests = response.data;
          })
          .catch((error) => {
            console.error(error);
          });
      },
      acceptRequest(uuid) {
        axios
          .post(`/authors/${uuid}/accept_follow_request/`)
          .then(() => {
            this.fetchFollowRequests();
          })
          .catch((error) => {
            console.error(error);
          });
      },
      declineRequest(uuid) {
        axios
          .post(`/authors/${uuid}/decline_follow_request/`)
          .then(() => {
            this.fetchFollowRequests();
          })
          .catch((error) => {
            console.error(error);
          });
      },
    },
  };
  </script>
  