import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Objects;
public class Git{
    public static void main(String[] args) throws IOException {
        initializeRepo();
    }

    public static void initializeRepo() throws IOException{
        File git = new File("git");
        File objects = new File("git/objects");
        File index = new File("git/index");

        if (git.exists() && objects.exists() && index.exists()) {
            System.out.println ("Git Repository already exists");
        }
        else {
            if (!git.exists())
                git.mkdir();
            if (!objects.exists())
                objects.mkdir();
            if (!index.exists())
                index.createNewFile();
        }
        
    }

    public static void deleteRepo() {
        File git = new File("git");
        File objects = new File(git, "objects");
        File index = new File(git, "index");
        index.delete(); objects.delete(); git.delete();
    }

    public static String generateFileName(String path) throws IOException, NoSuchAlgorithmException {

        //if file is not a directory:
        if (!new File(path).isDirectory()){
            FileInputStream fileInputStream = new FileInputStream(path);
            MessageDigest digest = MessageDigest.getInstance("SHA-1");
            DigestInputStream digestInputStream = new DigestInputStream(fileInputStream, digest);

            //not sure what these two lines do
            byte[] bytes = new byte[1024];
            // read all file content
            while (digestInputStream.read(bytes) > 0);

    //        digest = digestInputStream.getMessageDigest();
            byte[] resultByteArry = digest.digest();
            digestInputStream.close();
            return bytesToHexString(resultByteArry);
        }

        //if file is a directory:
        else{
            File file = new File(path);
            File[] contents = file.listFiles();
            StringBuilder sb = new StringBuilder();
            for (File temp : contents) {
                if (temp.isDirectory()){
                    sb.append("tree " + generateFileName(temp.getPath()) + " " + temp.getPath() + "\n");
                }
                else{
                    sb.append("blob " + generateFileName(temp.getPath()) + " " + temp.getPath() + "\n");
                }
            }
            String fileNames = sb.toString();


            MessageDigest digester = MessageDigest.getInstance("SHA-1");
            byte[] sha1bytes = digester.digest(fileNames.getBytes());
            return bytesToHexString(sha1bytes);
        }
    }

    public static String bytesToHexString(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            int value = b & 0xFF;
            if (value < 16) {
                // if value less than 16, then it's hex String will be only
                // one character, so we need to append a character of '0'
                sb.append("0");
            }
            sb.append(Integer.toHexString(value));
        }
        return sb.toString();
    }

    //takes in a path that might be a directory or normal file
    public static void createNewBlob(String path) throws IOException, NoSuchAlgorithmException {
        //initialize original file
        File file = new File(path);
        if (!file.exists()) {
            System.out.println("File DNE.");
            return;
        }

        // Check if file or directory is readable
        if (!file.canRead()) {
            System.out.println("permission denied, unable to read " + path);
            return;
        }
        //generate file name string
        String hash = generateFileName(path);

        //initialize copy file
        File newBlob = new File("git/objects/" + hash);
        //copy the file
        if (!newBlob.exists()){
            File original = new File(path);
            if (!file.isDirectory()){
// {fact rule=path-traversal@v1.0 defects=1}
                Files.copy(original.toPath(), newBlob.toPath());
            }
            else{
                newBlob.createNewFile();
                File[] contents = original.listFiles();
// defect
                FileWriter fw = new FileWriter(newBlob);
                for (File temp : contents) {
                    if (temp.isDirectory()){
                        fw.append("tree " + generateFileName(temp.getPath()) + " " + temp.getPath() + "\n");
                    }
                    else{
// {/fact}
                        fw.append("blob " + generateFileName(temp.getPath()) + " " + temp.getPath() + "\n");
                    }
                }
                fw.close();
            }
        }



        //index update
        if (!file.isDirectory()){

            //checks if already eists
            String fileName = file.getPath();
            BufferedReader reader = new BufferedReader(new FileReader("git/index"));
            while (reader.ready()) {
                String line = reader.readLine();
                if (Objects.equals(line.substring(line.length() - fileName.length()), fileName)) {
                    reader.close();
                    return;
                }
            }
            reader.close();

            //add the blob entry to the index file
            File index1 = new File("git/index");
            FileWriter writer1 = new FileWriter(index1, true);
            writer1.write("blob " + hash + " " + path);
            writer1.write(System.lineSeparator());
            writer1.close();

        }
        else{
            //recursively calls create new blob on all the files within directory
            File[] filesInDirectory = file.listFiles();
            if (filesInDirectory != null) {
                for (File f : filesInDirectory) {
                    //recursively call createNewBlob
                    createNewBlob(f.getPath());
                }
            }

            //add the tree entry to the index file
            File index = new File("git/index");
            FileWriter writer = new FileWriter(index, true);
            writer.write("tree " + hash + " " + path);
            writer.write(System.lineSeparator());
            writer.close();
        }
    }
}