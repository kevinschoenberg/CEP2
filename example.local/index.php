<!DOCTYPE html>
<html>
    <head>
        <style>
            <?php
                include "style.css";
            ?>
        </style>
    </head>
        <body>
            <table>
                <tr>
                    <th>Id</th>
                    <th>Time stamp</th>
                    <th>Event</th>
                    <th>Event Chain </th>
                </tr>
                <h1>KitchenGuard Events</h1>
                <?php
                    $servername = "127.0.0.1";
                    $username = "root";
                    $password = "cep2";
                    $dbname = "kitchenguearddb";

                    // Database connection
                    $conn = new mysqli($servername, $username, $password, $dbname);
                    // Check connection
                    if ($conn->connect_error) {
                    die("Connection failed: " . $conn->connect_error);
                    }

                    $sql = "SELECT Timestamp, Eventtype, IdChain, id FROM events ORDER BY id DESC";
                    $result = $conn->query($sql);
                    
                    if ($result->num_rows > 0) {
                    // output data of each row
                    while($row = $result->fetch_assoc()) {
                        $time = gmdate("Y-m-d H:i:s", $row["Timestamp"]);
                        echo "<tr>";
                        echo "<td>" . $row['id'] . "</td>";
                        echo "<td>" . $time . "</td>";
                        echo "<td>" . $row['Eventtype'] . "</td>";
                        echo "<td>" . $row["IdChain"] . "</td>";
                        echo "</tr>";
                    }

                    }
                    else {
                    echo "0 results";
                    }
                    $conn->close();
                    ?>
            </table>

