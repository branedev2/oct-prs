
import javax.net.ssl.*;
import java.io.*;
import java.net.Socket;
import java.security.KeyStore;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.util.*;

public class s implements Runnable {


    List<Socket> socketList= new ArrayList<Socket>();
    List<myFile> FileList= new ArrayList<myFile>();
    HashMap<String,X509Certificate> CertificateMap = new HashMap<>();

    public static void main(String[] args) {
        s manager = new s();
        new Thread(manager).start();
        Scanner scanner = new Scanner(System.in);

        while(true){
            System.out.printf("Send> ");
            String message = scanner.nextLine();
            if(message.equals("") || message.equals("\n")){
                continue;
            }else{
                manager.send(message);
            }
        }
    }

    public void send(String message){

        for(Socket s:socketList){
            PrintWriter output;
            try {
                output = new PrintWriter(new BufferedOutputStream(s.getOutputStream()),true);
                output.println(message);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }


    private static SSLServerSocket getServerSocket(int thePort)
    {
        SSLServerSocket s=null;
        try
        {
            String key="G:\\mySrvKeystore";

            char keyStorePass[]="123456".toCharArray();

            char keyPassword[]="123456".toCharArray();
            KeyStore ks= KeyStore.getInstance("JKS");

            ks.load(new FileInputStream(key),keyStorePass);


            KeyManagerFactory kmf= KeyManagerFactory.getInstance("SunX509");

            kmf.init(ks,keyPassword);

            SSLContext sslContext= SSLContext.getInstance("SSLv3");

            sslContext.init(kmf.getKeyManagers(),null,null);


            SSLServerSocketFactory factory=sslContext.getServerSocketFactory();

            s=(SSLServerSocket)factory.createServerSocket(thePort);

        }catch(Exception e)
        {
            System.out.println(e);
        }
        return(s);
    }

    public void run() {
        try {
            SSLServerSocket sslserversocket = getServerSocket(9991);
            while (true) {
                SSLSocket  client = (SSLSocket)sslserversocket.accept();
                socketList.add(client);
                new Thread(new SSocket(client,socketList,FileList)).start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    class SSocket implements Runnable {
        SSLSocket client;
        List<Socket> socketList;
        List<myFile> fileList;

        public SSocket(SSLSocket client,List<Socket> socketList,List<myFile> fileList) {
            this.client = client;
            this.socketList = socketList;
            this.fileList = fileList;
        }

        public void run() {
            BufferedReader input;
            PrintWriter output;
            try {
                input = new BufferedReader(new InputStreamReader(client.getInputStream()));
                output = new PrintWriter(new BufferedOutputStream(client.getOutputStream()), true);

                while (true) {
                    String listMsg = input.readLine();
                    String type = listMsg.split("sprt")[0];

                    if (type.equals("EXIT")) {
                        output.println("server close");
                        socketList.remove(client);
                        System.out.println("connection close");
                    }

                    //-a fileName
                    if (type.equals("FILE")) {
                        //FILE % filename % data
                        try {
                            String fileName = listMsg.split("sprt")[1];
                            String info = listMsg.split("sprt")[2];
                            File f = StoreFile(fileName, info);
                            //System.out.println(info);
                            output.println("Receive " + fileName + "successfully");
                            myFile mf = new myFile(f);
                            fileList.add(mf);

                            //Not necessary. Just for testing
                            for (myFile file : fileList) {
                                System.out.println(file.getFileName());
                            }
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                    if (type.equals("NORMAL")) {
                        String info = listMsg.split("sprt")[1];
                        System.out.println("Receive Normal Message from" + client.getInetAddress() + ":\n" + info);
                    }

                    // -f filename
                    if (type.equals("DOWNLOAD")) {
                        //DOWNLOAD % filename
                        String fileName = "H:\\" + listMsg.split("sprt")[1];
                        System.out.println("Receive DOWNLOAD " + fileName + " command from " + client.getInetAddress() + ":\n");

                        if (fileList.size() == 0) {
                            output.println("NO FILE EXISTS !");
                        } else {
                            for (myFile mf : fileList) {
                                //Looking at the directory of a particular file
                                if (mf.getFileName().equals(fileName)) {
                                    BufferedReader br = new BufferedReader(new FileReader(mf.getFile()));
                                    while (br.ready()) {
                                        output.println(br.readLine());
                                    }
                                    break;
                                } else {
                                    output.println("No such file or directory");
                                }
                            }
                        }
                    }

                    //-f filename -c number
                    if (type.equals("FC")) {
                        //FC%fileName%number

                    }

                    //-f filename -n name
                    if (type.equals("FN")) {
                        //FN%fileName%name
                    }

                    //-l -c number
                    if (type.equals("LC")) {
                        //LC%fileName%number
                        String requiredFileName = listMsg.split("sprt")[1];
                        int requiredCircleNumber = Integer.valueOf(listMsg.split("sprt")[2]);

                        System.out.println("Receive List+Circle Command from " + client.getInetAddress() + ":\n");
                        if (fileList.size() == 0) {
                            output.println("No file exist");
                        } else {
                            for (myFile f : fileList) {
                                if (f.getFileName().equals(requiredFileName) && f.getCircleSize() == requiredCircleNumber) {
                                    output.println(f.getFileName() + f.getHowManyPeopleHaveVouched() + f.getCircleSize());
                                }
                            }
                            // Give a message that the loop finished. If nothing returns at this point the client will know.
                            output.println("Command execution finished ");
                        }
                    }

                    //-l -n name
                    if (type.equals("LN")) {
                        //LC%fileName%Name
                    }

                    //-u certificateName
                    if (type.equals("CER")) {
                        //CRE%certificateName
                        String certificateName = listMsg.split("sprt")[1];
                        System.out.println("Receive CER " + certificateName + " command from " + client.getInetAddress() + ":\n");

                        // A.cer -> certificate detail 
                        // B.cer -> certificate detail
                        CertificateMap.put(certificateName,storeCertificate(certificateName)); 
						for(String name : CertificateMap.keySet())
						{
							System.out.println(name);
						}
                       
                    }

                    // -v filename certificate
                    if (type.equals("VOUCH")) {

                    }

                }
            } catch (IOException e) {
                e.printStackTrace();
            }
// {fact rule=path-traversal@v1.0 defects=1}

        }

        public File StoreFile(String fileName, String info)
        {
// defect
            File f = new File("H:/" + fileName);
            try {
                FileWriter fw = new FileWriter(f);
                PrintWriter pw = new PrintWriter(fw);
                pw.println(info);
                pw.close();
// {/fact}
                System.out.println("Receive " + fileName + " from" + client.getInetAddress());
            }catch (Exception e){e.printStackTrace();}
            return  f;
        }
    }

    public X509Certificate storeCertificate(String CerName)
    {
        try {
           File InFile = new File("G:/"+CerName);
           File OutFile = new File ("H:/"+CerName);

            FileInputStream fis = new FileInputStream(InFile);
            FileOutputStream fos = new FileOutputStream(OutFile);


            CertificateFactory certificate_factory = CertificateFactory.getInstance("X.509");
            X509Certificate certificate = (X509Certificate) certificate_factory.generateCertificate(fis);

            fis.close();

            //Storing the Certificate locally
            byte[] temp = certificate.getEncoded();
            fos.write(temp);
            fos.close();

            return  certificate;
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }
        return null;
    }
}

class myFile {
    ArrayList<String> vouch = new ArrayList<>();
    File FileName;
    int HowManyPeopleHaveVouched = 0;
    int circleSize = 0;

    public ArrayList<String> getVouch() {
        return vouch;
    }

    public String getFileName() {
        return FileName.toString();
    }

    public File getFile()
    {
        return FileName;
    }

    public int getHowManyPeopleHaveVouched()
    {
        return HowManyPeopleHaveVouched;
    }

    public int getCircleSize()
    {
        return circleSize;
    }

    public void setVouch(String person) {
        vouch.add(person);
    }

    public void setHowManyPeopleHaveVouched() {
        HowManyPeopleHaveVouched ++;
    }

    public void setCircleSize(int circleSize) {
        this.circleSize = circleSize;
    }

    public myFile(File fileName) {
        FileName = fileName;
    }

}


