# AVHelper Database Schema

## Database Structure

The AVHelper database contains 4 main tables for managing adult video content and related data.

### Tables

#### 1. actress
Stores information about actresses/performers.

```sql
CREATE TABLE actress (
	id int NOT NULL,
	name varchar(30),
	rating varchar(3),
	face varchar(30),
	"style" varchar(30),
	breast varchar(30),
	waist varchar(30),
	legs varchar(30),
	body varchar(30),
	hair varchar(30),
	features varchar(100),
	role_type varchar(30),
	common varchar(200),
	is_delete tinyint,
	data_date TIMESTAMP(26),
	update_date TIMESTAMP(26),
	alias varchar(100)
);
```

**Fields:**
- `id`: Primary key, unique identifier
- `name`: Actress name (max 30 chars)
- `rating`: Rating value (max 3 chars)
- `face`, `style`, `breast`, `waist`, `legs`, `body`, `hair`: Physical characteristics (max 30 chars each)
- `features`: Additional features description (max 100 chars)
- `role_type`: Type of roles performed (max 30 chars)
- `common`: General comments (max 200 chars)
- `is_delete`: Soft delete flag
- `data_date`, `update_date`: Timestamp fields for data tracking
- `alias`: Alternative names (max 100 chars)

#### 2. nyaa_post
Stores torrent posts from Nyaa tracker.

```sql
CREATE TABLE nyaa_post (
	id int NOT NULL,
	category varchar(5),
	title varchar(300),
	torrent_url varchar(200),
	magnet varchar(3000),
	"size" varchar(15),
	pub_time TIMESTAMP(26),
	hash varchar(40),
	URL varchar(200),
	submitter varchar(30),
	grab_time TIMESTAMP(26),
	videoid varchar(100),
	video_quality int,
	info varchar(200)
);
```

**Fields:**
- `id`: Primary key
- `category`: Torrent category (max 5 chars)
- `title`: Post title (max 300 chars)
- `torrent_url`: Direct torrent download URL (max 200 chars)
- `magnet`: Magnet link (max 3000 chars)
- `size`: File size information (max 15 chars)
- `pub_time`: Publication timestamp
- `hash`: Torrent hash (40 chars)
- `URL`: Post URL (max 200 chars)
- `submitter`: Username who submitted (max 30 chars)
- `grab_time`: When data was scraped
- `videoid`: Associated video ID (max 100 chars)
- `video_quality`: Quality rating (integer)
- `info`: Additional information (max 200 chars)

#### 3. nyaa_post_trends
Tracks seeder/leecher statistics for torrent posts over time.

```sql
CREATE TABLE nyaa_post_trends (
	id int NOT NULL,
	postId int,
	seeder int,
	leecher int,
	complete int,
	data_time TIMESTAMP(26)
);
```

**Fields:**
- `id`: Primary key
- `postId`: Foreign key to nyaa_post.id
- `seeder`: Number of seeders
- `leecher`: Number of leechers
- `complete`: Number of completed downloads
- `data_time`: When statistics were recorded

#### 4. video
Main table storing video/movie information.

```sql
CREATE TABLE video (
	id varchar(60),
	idSeries varchar(30),
	idNumber varchar(30),
	dmmID varchar(15),
	javdbID varchar(20),
	pubDate TIMESTAMP(10),
	duration TIMESTAMP(16),
	title varchar(300),
	actress_name TEXT(32767),
	actressID varchar(20),
	rating float,
	isDownloaded tinyint,
	isIgnore tinyint,
	addDate TIMESTAMP(26),
	downloadDate TIMESTAMP(26),
	deleteDate TIMESTAMP(10),
	deleteReason TEXT(32767),
	remark TEXT(32767)
);
```

**Fields:**
- `id`: Primary key, video identifier (max 60 chars)
- `idSeries`: Series identifier (max 30 chars)
- `idNumber`: Video number within series (max 30 chars)
- `dmmID`: DMM (Digital Media Mart) identifier (max 15 chars)
- `javdbID`: JAVDB identifier (max 20 chars)
- `pubDate`: Publication date
- `duration`: Video duration
- `title`: Video title (max 300 chars)
- `actress_name`: Names of actresses (large text field)
- `actressID`: Related actress ID (max 20 chars)
- `rating`: User rating (float)
- `isDownloaded`: Download status flag
- `isIgnore`: Ignore flag for filtering
- `addDate`: When record was added
- `downloadDate`: When video was downloaded
- `deleteDate`: When record was marked for deletion
- `deleteReason`: Reason for deletion (large text field)
- `remark`: Additional notes (large text field)

## Relationships

- `nyaa_post_trends.postId` → `nyaa_post.id`
- `video.actressID` → `actress.id` (implied relationship)
- `nyaa_post.videoid` → `video.id` (implied relationship)