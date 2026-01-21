rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper function to check if user is admin
    function isAdmin() {
      return request.auth != null && request.auth.token.email == 'factoryfrequency@gmail.com';
    }
    
    // Tracks collection
    match /tracks/{trackId} {
      // Anyone can read approved tracks
      allow read: if resource.data.status == 'approved';
      
      // Admins can read all tracks (including pending/rejected)
      allow read: if isAdmin();
      
      // Authenticated users can create tracks (they auto-go to pending status)
      allow create: if request.auth != null
                    && request.resource.data.status == 'pending'
                    && request.resource.data.submittedBy == request.auth.uid;
      
      // Only admins can update track status (approve/reject)
      allow update: if isAdmin();
      
      // Only admins can delete tracks
      allow delete: if isAdmin();
    }
    
    // Users collection
    match /users/{userId} {
      // Users can read their own profile
      allow read: if request.auth != null && request.auth.uid == userId;
      
      // Users can create/update their own profile
      allow create, update: if request.auth != null && request.auth.uid == userId;
      
      // Admins can read all users
      allow read: if isAdmin();
    }
    
    // Ratings subcollection
    match /tracks/{trackId}/ratings/{ratingId} {
      // Anyone can read ratings for approved tracks
      allow read: if get(/databases/$(database)/documents/tracks/$(trackId)).data.status == 'approved';
      
      // Authenticated users can add ratings to approved tracks
      allow create: if request.auth != null
                    && get(/databases/$(database)/documents/tracks/$(trackId)).data.status == 'approved'
                    && request.resource.data.userId == request.auth.uid;
      
      // Users can update their own ratings
      allow update: if request.auth != null && resource.data.userId == request.auth.uid;
      
      // Admins can do anything with ratings
      allow read, write: if isAdmin();
    }
  }
}