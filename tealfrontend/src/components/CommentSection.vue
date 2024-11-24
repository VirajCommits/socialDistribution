<!-- src/components/CommentSection.vue -->
<template>
  <div class="comment-section">
    <h4 class="section-title">Comments ({{ comments.length }})</h4>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-circle-notch fa-spin"></i>
      <p>Loading comments...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="comments.length === 0" class="empty-state">
      <i class="fas fa-comment-slash"></i>
      <p>No comments yet. Be the first to comment!</p>
    </div>

    <!-- Comments List -->
    <div v-else class="comments-list">
      <ul>
        <li v-for="comment in comments" :key="comment.id" class="comment-item">
          <!-- Avatar and Author Name Container -->
          <div class="avatar-and-author">
            <img
              :src="comment.author.profileImage || defaultAvatar"
              alt="Commenter Avatar"
              class="comment-avatar"
            />
            <span class="comment-author">{{ comment.author.displayName }}</span>
          </div>

          <!-- Comment Text -->
          <div class="comment-details">
            <p class="comment-text">{{ comment.content }}</p>
          </div>

          <!-- Like Button for Each Comment -->
          <LikeButton :commentId="comment.id" />
        </li>
      </ul>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <i class="fas fa-check-circle"></i>
      {{ successMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMessage }}
    </div>

    <!-- Comment Form -->
    <div class="comment-form">
      <textarea
        v-model="newComment"
        placeholder="Write a comment..."
        rows="3"
        @keydown.enter.prevent="submitComment"
      ></textarea>
      <button @click="submitComment" :disabled="!newComment.trim()">
        <i class="fas fa-paper-plane"></i> Comment
      </button>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import LikeButton from "./LikeButton.vue";

export default {
  name: "CommentSection",
  props: {
    postId: {
      type: String,
      required: true,
    },
  },
  components: {
    LikeButton,
  },
  data() {
    return {
      comments: [],
      newComment: "",
      loading: true,
      errorMessage: "",
      successMessage: "",
      // Default avatar in case the commenter hasn't set one
      defaultAvatar:
        "https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg",
      user: null,
      authID: "",
    };
  },
  mounted() {
    this.initializeUser();
    this.fetchComments();
  },
  methods: {
    /**
     * Initializes user information from localStorage.
     * Extracts the current user's ID for further operations.
     */
    initializeUser() {
      try {
        this.user = JSON.parse(localStorage.getItem("user"));
        if (this.user && this.user.id) {
          this.authID = this.user.id.split("/").pop();
        } else {
          throw new Error("User information not found");
        }
      } catch (error) {
        console.error("Error initializing user:", error);
        this.errorMessage = "Failed to retrieve user information.";
      }
    },

    /**
     * Fetches comments associated with the given post ID.
     * Populates the comments array with fetched data.
     */
    // Fetch comments for the given post ID
    async fetchComments() {
      try {
        const apiUrl = `/posts/${encodeURIComponent(this.postId)}/comments/`;
        const response = await axios.get(apiUrl, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        this.comments = response.data || [];
        this.loading = false;
      } catch (error) {
        console.error("Error fetching comments:", error.response || error);
        this.errorMessage = "An error occurred while fetching comments.";
        this.loading = false;
      }
    },
    

    /**
     * Submits a new comment.
     * After successfully creating the comment, it distributes the comment to relevant inboxes.
     */
    async submitComment() {
      if (!this.newComment.trim()) return;

      try {
        // Ensure the user is authenticated
        if (!this.authID) {
          this.errorMessage = "User not authenticated.";
          return;
        }

        // Prepare the comment payload
        const apiUrl = `/posts/${encodeURIComponent(this.postId)}/comment/`;
        const payload = {
          content: this.newComment.trim(),
          contentType: "text/plain",
          author_id: this.authID, // Include the author ID
        };

        // Make the POST request to submit the comment
        const response = await axios.post(apiUrl, payload, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${localStorage.getItem("token")}`, // Include the authentication token
          },
        });

        // Clear the input field and fetch updated comments
        this.newComment = "";
        this.fetchComments();

        // Distribute the comment via inbox
        await this.distributeComment(response.data);
      } catch (error) {
        console.error("Error submitting comment:", error.response || error);
        this.errorMessage = "An error occurred while submitting the comment.";
      }
    },

    /**
     * Distributes the newly created comment to relevant authors' inboxes.
     * @param {Object} commentData - The data of the newly created comment.
     */
    async distributeComment(commentData) {
      try {
        // Fetch the post details to get the author's information and visibility
        const postApiUrl = `/posts/${encodeURIComponent(this.postId)}/`;
        console.log("<<<<<<<<<<<<>>>>>>>>>>>>>>>>>" , postApiUrl)
        const postResponse = await axios.get(postApiUrl, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        const post = postResponse.data;

        if (!post) {
          console.warn("Post details not found. Skipping comment distribution.");
          return;
        }

        const postAuthorId = post.author.id.split("/").pop();
        const postVisibility = post.visibility || "PUBLIC";

        // Fetch all authors (or fetch only relevant authors based on visibility)
        const authorsResponse = await axios.get("/authors/", {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        const authors = authorsResponse.data;
        console.log("AUTHORS IN COMMENT SECTION:===========" , authors)

        // Current user's ID
        const currentAuthorId = this.authID;

        // Track which authors have received the notification to prevent duplicates
        const processedAuthors = new Set([currentAuthorId]); // Initialize with current author

        // Determine the list of authors to send the comment to based on post visibility
        let targetAuthors = [];

        console.log("COMMENT SECTION -------------- ")

        switch (postVisibility) {
            case "PUBLIC": {
                // Visible to everyone except the current author
                const ourHost = this.user.host;
    
                // Filter out authors who:
                // 1. Are not the current author
                // 2. Don't have the same host as our user
                targetAuthors = authors.filter(author => 
                    author.uuid !== currentAuthorId && 
                    author.host !== ourHost
                );
                console.log("TARGET AUTHORS IN COMMENT SECTION:" , targetAuthors)
                break;
            }
            case "FRIENDS": {
                try {
                    console.log("Checking FRIENDS visibility");
                    const currentUser = JSON.parse(localStorage.getItem('user'));
                    
                    // First, check if the current user is a follower of the post author
                    const postAuthorFollowers = await this.getFollowers(postAuthorId);
                    const isFollower = postAuthorFollowers.some(
                        follower => follower.uuid === currentUser.uuid
                    );
                    
                    // Then check if the post author follows the current user
                    const currentUserFollowers = await this.getFollowers(currentUser.uuid);
                    const isFollowed = currentUserFollowers.some(
                        follower => follower.uuid === postAuthorId
                    );
                    
                    console.log('Is follower:', isFollower);
                    console.log('Is followed:', isFollowed);
                    
                    // Only allow access if there's a mutual follow relationship
                    if (!isFollower || !isFollowed) {
                        console.log('Not a mutual friend - access denied');
                        throw new Error('You must be friends with the author to view this post');
                    }
                    
                    // If we get here, they are friends, so include in targetAuthors
                    targetAuthors = [currentUser];
                    
                } catch (error) {
                    console.error('Error in FRIENDS visibility check:', error);
                    throw error;
                }
                break;
            }
            case "UNLISTED": {
                // Visible to all followers of the post author
                targetAuthors = await this.getFollowers(postAuthorId);
                break;
            }
            default: {
                // Default to PUBLIC if visibility is undefined
                targetAuthors = authors.filter(
                    (author) => author.id.split("/").pop() !== currentAuthorId
                );
                break;
            }
        }

        console.log("TARGET AUTHORS IN COMMENT SECTION before for loop:" , targetAuthors)
        // Distribute the comment to the target authors
        for (const author of targetAuthors) {
          console.log("AUTHOR IN COMMENT SECTION:" , author)
          const targethost = author.id.split('/authors/')[0];
          const authorId = author.id.split("/").pop();
          if (!processedAuthors.has(authorId)) {
            await this.sendCommentToInbox(authorId, commentData, post, targethost);
            processedAuthors.add(authorId);
          }
        }

        console.log("Comment distribution completed.");
      } catch (error) {
        console.error("Error distributing comment:", error);
        // Optionally, set an error message or handle it as needed
      }
    },

    /**
     * Sends the comment to a specific author's inbox.
     * @param {String} authorId - The UUID of the target author.
     * @param {Object} commentData - The data of the comment.
     * @param {Object} postData - The data of the post the comment belongs to.
     */
    async sendCommentToInbox(authorId, commentData, postData, targethost) {
      try {
        console.log("SENDING COMMENT TO INBOX IN COMMENT SECTION:" , authorId, commentData, postData, targethost)
        const inboxUrl = `${targethost}service/api/authors/${authorId}/inbox/`;

        const payload = {
          type: "comment",
          id: commentData.id,
          content: commentData.content,
          contentType: commentData.contentType,
          published: commentData.published || new Date().toISOString(),
          author: {
            type: "author",
            id: this.user.id,
            host: this.user.host,
            displayName: this.user.displayName,
            page: this.user.page,
            github: this.user.github,
            profileImage: this.user.profileImage,
          },
          post: {
            id: postData.id,
            title: postData.title,
            description: postData.description,
            contentType: postData.contentType,
            content: postData.content,
            published: postData.published,
            visibility: postData.visibility,
            author: postData.author,
          },
        };

        console.log(`Sending comment to inbox of author ${authorId}:`, payload);

        const response = await axios.get('/connected-nodes/', {
          headers: { Authorization: `Token ${this.token}` },
        });
        const connectedNodes = response;
        const connected_nodes = response.data;
        console.log("CONNECTED NODES IN COMMENT SECTION:" , connectedNodes)
        console.log("CONNECTED NODES DATA IN COMMENT SECTION:" , connected_nodes)
        console.log("TARGET HOST IN COMMENT SECTION:" , targethost)

        console.log("HOST IN COMMENT SECTION:" , targethost)
        const targetNode = connected_nodes.find(node => node.url === targethost);
        console.log("TARGET NODE IN COMMENT SECTION:" , targetNode)
        const credentials = btoa(`${targetNode.username}:${targetNode.password}`);

        await axios.post(inboxUrl, payload, {
          headers: {
            Authorization: `Basic ${credentials}`,
            "Content-Type": "application/json",
          },
          withCredentials: true,
        });
      } catch (error) {
        console.error(`Error sending comment to author ${authorId}'s inbox:`, error);
        throw error; // Re-throw to handle in distributeComment
      }
    },

    /**
     * Fetches the followers of a given author.
     * Used when the post visibility is set to FRIENDS.
     * @param {String} authorId - The UUID of the author whose followers are to be fetched.
     * @returns {Array} - An array of follower authors.
     */
    async getFollowers(authorId) {
      try {
        const followersApiUrl = `/authors/${encodeURIComponent(authorId)}/followers/`;
        const response = await axios.get(followersApiUrl, {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
          },
        });
        return response.data || [];
      } catch (error) {
        console.error("Error fetching followers:", error);
        return [];
      }
    },
    async getFollowing(authorId) {
        try {
            const response = await axios.get(`/authors/${authorId}/following/`);
            return response.data;
        } catch (error) {
            console.error(`Error getting following for author ${authorId}:`, error);
            return [];
        }
    }
  },
};
</script>

<style scoped>
/* Comment Section Container */
.comment-section {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  max-width: 600px;
  margin: 0 auto;
}

/* Section Title */
.section-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #333333;
  margin-bottom: 1rem;
}

/* Loading and Empty States */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #888888;
  margin-bottom: 1rem;
}

.loading-state i,
.empty-state i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

/* Comments List */
.comments-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* Individual Comment Item */
.comment-item {
  display: flex;
  align-items: center; /* Vertically centers avatar and author */
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

/* Avatar and Author Name Container */
.avatar-and-author {
  display: flex;
  align-items: center; /* Vertically centers the author name with the avatar */
  margin-right: 1rem;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 0.75rem;
}

.comment-author {
  font-weight: bold;
  color: #333333;
  text-align: left; /* Ensures left alignment */
}

/* Comment Details (Text and Time) */
.comment-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start; /* Aligns text to the left */
  width: 100%;
}

.comment-text {
  font-size: 0.95rem;
  color: #333333;
  margin: 0.5rem 0;
  text-align: left; /* Aligns text to the left */
  max-width: 400px; /* Limits the width for better readability */
  width: 100%; /* Ensures the text takes the available width */
}

/* Success Message */
.success-message {
  display: flex;
  align-items: center;
  background-color: #dff0d8;
  color: #3c763d;
  padding: 0.75rem 1rem;
  border: 1px solid #d6e9c6;
  border-radius: 8px;
  margin-top: 1rem;
}

.success-message i {
  margin-right: 0.5rem;
}

/* Error Message */
.error-message {
  display: flex;
  align-items: center;
  background-color: #ffe5e5;
  color: #cc0000;
  padding: 0.75rem 1rem;
  border: 1px solid #e74c3c;
  border-radius: 8px;
  margin-top: 1rem;
}

.error-message i {
  margin-right: 0.5rem;
}

/* Comment Form */
.comment-form {
  display: flex;
  flex-direction: column;
  margin-top: 1.5rem;
}

.comment-form textarea {
  resize: vertical;
  min-height: 60px;
  padding: 0.75rem;
  border: 1px solid #dddddd;
  border-radius: 8px;
  font-size: 1rem;
  color: #333333;
  margin-bottom: 0.75rem;
  transition: border-color 0.2s;
}

.comment-form textarea:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 5px rgba(74, 144, 226, 0.5);
}

.comment-form button {
  align-self: flex-end;
  background-color: #4a90e2;
  color: #ffffff;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.comment-form button:hover {
  background-color: #357abd;
}

.comment-form button:disabled {
  background-color: #a0c4e8;
  cursor: not-allowed;
}

/* Responsive Design for Smaller Screens */
@media (max-width: 600px) {
  .comment-section {
    padding: 1rem;
  }

  .comment-avatar {
    width: 35px;
    height: 35px;
  }

  .comment-author {
    font-size: 0.95rem;
  }

  .comment-text {
    max-width: 100%; /* Allow full width on small screens */
    padding: 0 1rem; /* Add some padding for better appearance */
  }

  .comment-form button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
}
</style>
