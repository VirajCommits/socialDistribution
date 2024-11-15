from django.test import TestCase, Client

from .models import Author, Post, Comment, Like, FollowRequest
from django.utils import timezone
import base64

# Create your tests here.

class identityTests(TestCase):
    
    def test_author_id_page(self):      # Identity1, Identity3
        author = Author.objects.create(username="testuser", displayName="Test User")
        
        self.assertEqual(author.id, f"http://social-distribution-1-3adb84f120d9.herokuapp.com/authors/{author.uuid}")
        self.assertEqual(author.page, f"http://social-distribution-1-3adb84f120d9.herokuapp.com/authors/{author.username}")
    
    def test_multiple_authors(self):        # Identity2
        author1 = Author.objects.create(username="author1", displayName="Author 1")
        author2 = Author.objects.create(username="author2", displayName="Author 2")
        
        self.assertNotEqual(author1.id, author2.id)
        self.assertNotEqual(author1.page, author2.page)
        
        expected_host = "http://social-distribution-1-3adb84f120d9.herokuapp.com/authors/"
        self.assertTrue(author1.id.startswith(expected_host))
        self.assertTrue(author2.id.startswith(expected_host))
        
        authors = Author.objects.all()
        self.assertEqual(authors.count(), 2)
        self.assertIn(author1, authors)
        self.assertIn(author2, authors)
        
class postingTests(TestCase):
    def test_create_post_plain(self):      # Posting1, Posting6
        author = Author.objects.create(username="testauthor", displayName="Test Author")
        post = Post.objects.create(
            author=author,
            title="My First Post",
            content="This is the content of my first post!",
            contentType="text/plain",
            visibility="PUBLIC",
            published=timezone.now()
        )
        
        self.assertIsNotNone(post.id)
        self.assertEqual(post.author, author)
        self.assertEqual(post.title, "My First Post")
        self.assertEqual(post.content, "This is the content of my first post!")
        self.assertEqual(post.contentType, "text/plain")
        self.assertEqual(post.visibility, "PUBLIC")
        
        posts = Post.objects.filter(author=author)
        self.assertEqual(posts.count(), 1)
        self.assertIn(post, posts)
        
    def test_edit_post(self):       # Posting3
        author = Author.objects.create(username="testauthor", displayName="Test Author")
        post = Post.objects.create(
            author=author,
            title="Original Title",
            content="This is the original content.",
            contentType="text/plain",
            visibility="PUBLIC",
            published=timezone.now()
        )
        
        post.title = "Updated Title"
        post.content = "This is the updated content."
        post.save()
        
        updated_post = Post.objects.get(id=post.id)
        self.assertEqual(updated_post.title, "Updated Title")
        self.assertEqual(updated_post.content, "This is the updated content.")
        
    def test_create_post_common(self):      # Posting5
        author = Author.objects.create(username="testauthor", displayName="Test Author")
        commonmark_content = "# My Formatted Post\n\n- Item 1\n- Item 2\n\nThis is **bold** text."
        post = Post.objects.create(
            author=author,
            title="Formatted Post",
            content=commonmark_content,
            contentType="text/markdown",
            visibility="PUBLIC",
            published=timezone.now()
        )
        
        self.assertEqual(post.contentType, "text/markdown")
        self.assertEqual(post.content, commonmark_content)
        
        posts = Post.objects.filter(author=author, contentType="text/markdown")
        self.assertEqual(posts.count(), 1)
        self.assertIn(post, posts)
        
    def test_create_post_image(self):        # Posting7
        author = Author.objects.create(username="testauthor", displayName="Test Author")
        
        # Sample base64-encoded image data (representing a small black square PNG image)
        image_data = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\xdac\xf8\x0f\x00\x01\x01\x01\x00\x18\xdd\x03\xbe\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')
        
        post = Post.objects.create(
            author=author,
            title="Image Post",
            content=image_data,
            contentType="image/png;base64",
            visibility="PUBLIC",
            published=timezone.now()
        )
        
        self.assertEqual(post.contentType, "image/png;base64")
        self.assertEqual(post.content, image_data)
        
        posts = Post.objects.filter(author=author, contentType="image/png;base64")
        self.assertEqual(posts.count(), 1)
        self.assertIn(post, posts)
        
    def test_delete(self):      # Posting9
        author = Author.objects.create(username="testauthor", displayName="Test Author")
        post = Post.objects.create(
            author=author,
            title="Post to Delete",
            content="This post will be deleted.",
            contentType="text/plain",
            visibility="PUBLIC",
            published=timezone.now()
        )
        
        post_id = post.id
        post.delete()

        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=post_id)
            
class readingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Author.objects.create_user(username="user", password="password", displayName="User")
        self.followed_author = Author.objects.create(username="followed_author", displayName="Followed Author")
        
        self.user.following.add(self.followed_author)

    def test_show_public_unlisted_friends(self):        # Reading1.1, Reading1.2
        public_post = Post.objects.create(
            author=self.followed_author,
            title="Public Post",
            content="This is a public post.",
            contentType="text/plain",
            visibility="PUBLIC",
            published=timezone.now()
        )
        
        friends_post = Post.objects.create(
            author=self.followed_author,
            title="Friends-Only Post",
            content="This is a friends-only post.",
            contentType="text/plain",
            visibility="FRIENDS",
            published=timezone.now()
        )

        private_post = Post.objects.create(
            author=self.followed_author,
            title="Private Post",
            content="This is a private post.",
            contentType="text/plain",
            visibility="PRIVATE",
            published=timezone.now()
        )

        stream = Post.objects.filter(
            visibility__in=["PUBLIC", "FRIENDS"],
            author__in=self.user.following.all()
        ).order_by('-published')
        
        self.assertIn(public_post, stream)
        self.assertIn(friends_post, stream)
        self.assertNotIn(private_post, stream)

    def test_sorted_recent_edit(self):        # Reading1.3
        post = Post.objects.create(
            author=self.followed_author,
            title="Original Post",
            content="Original content.",
            contentType="text/plain",
            visibility="PUBLIC",
            published=timezone.now()
        )
        
        post.title = "Updated Post"
        post.content = "Updated content."
        post.save()

        stream_post = Post.objects.get(id=post.id)
        self.assertEqual(stream_post.title, "Updated Post")
        self.assertEqual(stream_post.content, "Updated content.")

    def test_no_deleted(self):       # Reading1.4
        post = Post.objects.create(
            author=self.followed_author,
            title="To be deleted",
            content="This post will be deleted.",
            contentType="text/plain",
            visibility="PUBLIC",
            published=timezone.now()
        )
        post_id = post.id
        post.delete()

        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=post_id)

    def test_sorted_recent(self):      # Reading2
        old_post = Post.objects.create(
            author=self.followed_author,
            title="Old Post",
            content="This is an old post.",
            contentType="text/plain",
            visibility="PUBLIC",
            published=timezone.now() - timezone.timedelta(days=1)
        )
        
        new_post = Post.objects.create(
            author=self.followed_author,
            title="New Post",
            content="This is a new post.",
            contentType="text/plain",
            visibility="PUBLIC",
            published=timezone.now()
        )
        
        stream = Post.objects.filter(
            visibility="PUBLIC",
            author__in=self.user.following.all()
        ).order_by('-published')
        
        self.assertEqual(stream[0], new_post)
        self.assertEqual(stream[1], old_post)
        
class visibilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create_user(username="author", password="password", displayName="Author")
        self.friend = Author.objects.create_user(username="friend", password="password", displayName="Friend")
        self.follower = Author.objects.create_user(username="follower", password="password", displayName="Follower")
        
        self.author.followers.add(self.friend)
        self.friend.followers.add(self.author)
        self.follower.following.add(self.author)
    
    def is_visible_to(self, post, viewer):
        if post.visibility == "PUBLIC":
            return True
        elif post.visibility == "UNLISTED":
            return viewer == post.author or viewer in post.author.followers.all()
        elif post.visibility == "FRIENDS":
            return viewer in post.author.followers.all() and post.author in viewer.followers.all()
        elif post.visibility == "PRIVATE":
            return viewer == post.author
        return False
    
    def test_public(self):      # Visibility1, Visibility6
        public_post = Post.objects.create(
            author = self.author,
            title = "Public Post",
            content = "This is a public post.",
            contentType = "text/plain",
            visibility = "PUBLIC",
            published = timezone.now()
        )

        self.assertTrue(self.is_visible_to(public_post, self.friend))
        self.assertTrue(self.is_visible_to(public_post, self.follower))

    def test_unlisted(self):        # Visiblity2, Visibility5
        unlisted_post = Post.objects.create(
            author = self.author,
            title = "Unlisted Post",
            content = "This is an unlisted post.",
            contentType = "text/plain",
            visibility = "UNLISTED",
            published = timezone.now()
        )

        self.assertTrue(self.is_visible_to(unlisted_post, self.friend))
        self.assertTrue(self.is_visible_to(unlisted_post, self.follower))
        self.assertTrue(self.is_visible_to(unlisted_post, self.author))

    def test_friends_only(self):        # Visibility3, Visibility4, Visibility8
        friends_post = Post.objects.create(
            author = self.author,
            title = "Friends-Only Post",
            content = "This is a friends-only post.",
            contentType = "text/plain",
            visibility = "FRIENDS",
            published = timezone.now()
        )

        self.assertTrue(self.is_visible_to(friends_post, self.friend))
        self.assertFalse(self.is_visible_to(friends_post, self.follower))

    def test_private(self):     # Visibility10
        private_post = Post.objects.create(
            author = self.author,
            title = "Private Post",
            content = "This is a private post.",
            contentType = "text/plain",
            visibility = "PRIVATE",
            published = timezone.now()
        )

        self.assertTrue(self.is_visible_to(private_post, self.author))
        self.assertFalse(self.is_visible_to(private_post, self.friend))
        self.assertFalse(self.is_visible_to(private_post, self.follower))

    def test_deleted(self):     # Visibility9
        deleted_post = Post.objects.create(
            author = self.author,
            title = "Deleted Post",
            content = "This post will be deleted.",
            contentType = "text/plain",
            visibility = "PUBLIC",
            published = timezone.now()
        )
        deleted_post.delete()

        self.assertFalse(deleted_post in Post.objects.filter(id=deleted_post.id))
        
class commentsTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(username="author1", displayName="Author One")
        self.friend = Author.objects.create(username="friend", displayName="Friend Author")
        self.follower = Author.objects.create(username="follower", displayName="Follower Author")
        
        self.author.followers.add(self.friend)
        self.friend.followers.add(self.author)
        
        self.public_post = Post.objects.create(
            author = self.author,
            title = "Public Post",
            content = "This is a public post.",
            contentType = "text/plain",
            visibility = "PUBLIC",
            published = timezone.now()
        )
        self.friends_post = Post.objects.create(
            author = self.author,
            title = "Friends-Only Post",
            content = "This is a friends-only post.",
            contentType = "text/plain",
            visibility = "FRIENDS",
            published = timezone.now()
        )

    def test_comment_on_accessible_post(self):      # Comments1
        comment = Comment.objects.create(
            post = self.friends_post,
            author = self.friend,
            content = "Nice post!"
        )
        
        self.assertEqual(comment.post, self.friends_post)
        self.assertEqual(comment.author, self.friend)
        self.assertEqual(comment.content, "Nice post!")
        
        comment2 = Comment.objects.create(
            post=self.public_post,
            author=self.follower,
            content="Great post!"
        )
        
        self.assertEqual(comment2.post, self.public_post)
        self.assertEqual(comment2.author, self.follower)
        self.assertEqual(comment2.content, "Great post!")

    def test_like_accessible_post(self):        # Comments2
        like = Like.objects.create(
            post=self.friends_post,
            author=self.friend
        )
        
        self.assertEqual(like.post, self.friends_post)
        self.assertEqual(like.author, self.friend)
        
        like2 = Like.objects.create(
            post=self.public_post,
            author=self.follower
        )
        
        self.assertEqual(like2.post, self.public_post)
        self.assertEqual(like2.author, self.follower)

    def test_view_likes_on_public_post(self):       # Comments3
        Like.objects.create(post=self.public_post, author=self.friend)
        Like.objects.create(post=self.public_post, author=self.follower)
        
        likes = Like.objects.filter(post=self.public_post)
        self.assertEqual(likes.count(), 2)
        self.assertIn(self.friend, [like.author for like in likes])
        self.assertIn(self.follower, [like.author for like in likes])

    def test_friends_only_comments_visibility(self):        # Comments4
        comment = Comment.objects.create(
            post = self.friends_post,
            author = self.friend,
            content = "Only friends should see this."
        )
        
        visible_comments_for_author = Comment.objects.filter(post=self.friends_post, author__in=[self.author, self.friend])
        self.assertIn(comment, visible_comments_for_author)
        
        visible_comments_for_follower = Comment.objects.filter(post=self.friends_post, author=self.follower)
        self.assertNotIn(comment, visible_comments_for_follower)
        
class followingfriendsTests(TestCase):
    def setUp(self):
        self.author1 = Author.objects.create(username="local_author", displayName="Local Author")
        self.author2 = Author.objects.create(username="remote_author", displayName="Remote Author")
        self.author3 = Author.objects.create(username="another_author", displayName="Another Author")

    def test_follow_local_author(self):     # Follow1
        self.author1.following.add(self.author2)
        self.assertIn(self.author2, self.author1.following.all())
        self.assertIn(self.author1, self.author2.followers.all())
        
    def test_approve_follow_request(self):     # Follow3
        follow_request = FollowRequest.objects.create(actor=self.author2, object=self.author1)
        follow_request.accepted = True
        follow_request.save()
        self.author1.followers.add(self.author2)
        self.assertTrue(follow_request.accepted)
        self.assertIn(self.author2, self.author1.followers.all())

    def test_deny_follow_request(self):     # Follow3
        follow_request = FollowRequest.objects.create(actor=self.author2, object=self.author1)
        follow_request.delete()
        self.assertNotIn(self.author2, self.author1.followers.all())
        self.assertFalse(FollowRequest.objects.filter(actor=self.author2, object=self.author1).exists())
        
    def test_retrieve_follow_requests(self):     # Follow4
        FollowRequest.objects.create(actor=self.author2, object=self.author1)
        follow_requests = FollowRequest.objects.filter(object=self.author1, accepted=False)
        self.assertEqual(follow_requests.count(), 1)
        self.assertEqual(follow_requests.first().actor, self.author2)

    def test_unfollow_author(self):     # Follow5
        self.author1.following.add(self.author2)
        self.author1.following.remove(self.author2)
        self.assertNotIn(self.author2, self.author1.following.all())
        self.assertNotIn(self.author1, self.author2.followers.all())

    def test_becoming_friends(self):     # Follow6
        self.author1.following.add(self.author2)
        self.author2.following.add(self.author1)
        self.assertTrue(self.author1.is_friend_with(self.author2))
        self.assertTrue(self.author2.is_friend_with(self.author1))

    def test_unfriend_author(self):     # Follow7
        self.author1.following.add(self.author2)
        self.author2.following.add(self.author1)
        self.author1.following.remove(self.author2)
        self.assertFalse(self.author1.is_friend_with(self.author2))
        self.assertFalse(self.author2.is_friend_with(self.author1))

    def test_retrieve_follower_following_and_friends_lists(self):     # Follow8
        self.author1.following.add(self.author2)
        self.author2.following.add(self.author1)
        self.author1.following.add(self.author3)

        self.assertIn(self.author2, self.author1.following.all())
        self.assertIn(self.author3, self.author1.following.all())
        self.assertIn(self.author1, self.author2.following.all())
        self.assertTrue(self.author1.is_friend_with(self.author2))
        self.assertFalse(self.author1.is_friend_with(self.author3))