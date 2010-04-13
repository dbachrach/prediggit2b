<?php

/*
CREATE TABLE `stories` (
  `id` integer primary key,
  `title` text NOT NULL,
  `description` text NOT NULL,
  `submit_date` integer NOT NULL,
  `status` text NOT NULL,
  `user_name` text NOT NULL,
  `topic` text NOT NULL,
  `container` text NOT NULL,
  `link` text NOT NULL
);
*/



require_once 'Services/Digg2.php';

$db = new SQLite3('digg.db');
if (!$db)
{
	echo "Connection failed \n";
	exit;
}

$DIGG_API = new Services_Digg2;

/* Make our connection times a little longer */
$request = new HTTP_Request2;
$request->setConfig(array('connect_timeout' => 10, 'timeout' => 10));
$DIGG_API->accept($request);
                                                 
getStories(0, 100, $DIGG_API);


function getStories($offset, $count, $api) {
	global $db;
	while ($offset < 5000000)
	{
	try 
	{   																			  
	    $params = array('offset' => $offset, 'count' => $count, 'max_submit_date' => "1242838800"); //1235887200 1236647229
	    $res = $api->story->getAll($params);
	    $stories = $res->stories;
	   
	    echo "(" . $res->offset . ", " . $res->count . ")\n";
	    $cnt = 0;
	    foreach ($stories as $story) 
	    {
	       echo "submit: " . sqlite_escape_string($story->submit_date) . "\n";
	    	$query = $db->prepare("INSERT INTO stories (id, title, description, submit_date, status, user_name, topic, container, link) 
	    	VALUES (:id, :title, :description, :submit_date, :status, :user_name, :topic, :container, :link)");
	        
	        $map = array(
	        			":id" => sqlite_escape_string($story->id),
	        			":title" => sqlite_escape_string($story->title), 
	        			":description" => sqlite_escape_string($story->description), 
	        			":submit_date" => sqlite_escape_string($story->submit_date), 
	        			":status" => sqlite_escape_string($story->status), 
	        			":user_name" => sqlite_escape_string($story->user->name),  
	        			":topic" => sqlite_escape_string($story->topic->name), 
	        			":container" => sqlite_escape_string($story->container->name), 
	        			":link" => sqlite_escape_string($story->link)
	        			);
	        			
	       	foreach(array_keys($map) as $key) {
	       	
	       		$query->bindValue($key,$map[$key]);
	       	}
	                   
	        $val = $query->execute();
	        if ($val == true)
	        {
	        	$cnt++;   	
	        }
	    }
	   
	    
	    echo "Inserted (" . $cnt . '/' .count($stories) . ") stories into database.\n";
	    
	    //sleep(30);
	    
	    //getStories($offset + $count, $count, $api);
	    $offset += $count;
	} 
	catch (Services_Digg2_Exception $error) 
	{
	    
	    if ($error->getMessage() == "Request timed out after 10 second(s)") {
	    	echo "Request timed out. Trying again...\n";
	    	//sleep(15);
	    	
	    	//getStories($offset, $count, $api);
	    	
	    }
	    else {
		    echo "error: " . $error->getMessage() . "\n";
		    $offset = 100000000;
		    break;
		   }
	    
	}
	}
}
?>
