import java.io.*;
import java.util.ArrayList;

import javax.swing.ImageIcon;
import javax.swing.JButton;

/**
 * Input/Output műveleteket megvalósitó osztály.
 */
public class IO {
	
	/**
	 * JButton-re képet betöltő metódus
	 * @param path A kép elérési útvonala
	 * @param btn A gomb, amire szeretnénk betölteni
	 */
	public static void loadButtonImage(String path, JButton btn) {
		try {
			btn.setIcon(new ImageIcon(path));
		}catch(Exception e) {
			PopUp.show("Error!", "Failed to load image: " + path);
		}
	}
	
	/**
	 * A program alapvető működéséhez szükséges mappákat, ha
	 * nem léteznek, létrehozó metódus. Az alapvető belépési profilt is
	 * itt hozzuk létre.
	 */
	public static void createFolders() {
		File profilesFolder = new File("Profiles");
		if(!profilesFolder.exists()) { 
			profilesFolder.mkdirs();
			ArrayList<AdminProfile> list = new ArrayList<AdminProfile>();
			list.add(new AdminProfile("admin", "admin"));
			IO.saveAdminProfiles(list);
		}
		File votesFolder = new File("Votes");
		if(!votesFolder.exists()) { votesFolder.mkdir(); }
		File keysFolder = new File("Votes/Keys");
		if(!keysFolder.exists()) { keysFolder.mkdir() ;}
	}
	
	/**
	 * Betölti az összes mentett profilt egy ArrayList-be
	 * @return Az összes mentett profil egy listába betöltve
	 */
	public static ArrayList<AdminProfile> loadAdminProfiles() {
		try {
			BufferedReader br = new BufferedReader(new FileReader("Profiles/AdminProfiles"));
			ArrayList<AdminProfile> l = new ArrayList<AdminProfile>();
			String line = br.readLine();
			while(line != null) {
				String[] splitLine = line.split(";");
				l.add(new AdminProfile(splitLine[0], splitLine[1]));
				line = br.readLine();
			}
			br.close();
			return l;
		}catch(Exception e) {
			PopUp.show("Error", "Unable to load administrator profiles!");
			return null;
		}
	}
	
	/**
	 * Profilokat elmentő metódus.
	 * @param profilesList Elmentendő profilokat tartalmazó lista
	 */
	public static void saveAdminProfiles(ArrayList<AdminProfile> profilesList) {
		try {
			BufferedWriter bw = new BufferedWriter(new FileWriter("Profiles/AdminProfiles"));
			int cntr = profilesList.size();
			for(AdminProfile ap : profilesList) {
				bw.write(ap.getUsername() + ";" + ap.getPassword());
				if(cntr != 1) {
					bw.newLine();
				}
				cntr--;
			}
			bw.close();
		}catch(Exception e) {
			PopUp.show("Error", "Unable to save administrator profiles!");
		}
	}
	
	/**
	 * Egy név alapján keresett szavazást betöltő metódus
	 * @param voteName A betöltendő szavazás neve
	 * @return A keresett Vote vagy, ha nem létezik null
	 */
	public static Vote loadVote(String voteName) {
		Vote v;
		try {
			BufferedReader br = new BufferedReader(new FileReader("Votes/" + voteName));
			String line = br.readLine();
			String[] fLine = line.split(";");
			
			ArrayList<Candidate> cl = new ArrayList<Candidate>();
			line = br.readLine();
			while(line != null) {	
				String[] cLine = line.split(";");
				cl.add(new Candidate(cLine[0], Integer.parseInt(cLine[1])));
				line = br.readLine();
			}
			
			v = new Vote(Integer.parseInt(fLine[0]), voteName, fLine[1], Integer.parseInt(fLine[2]), cl, IO.loadKeys(voteName));
			br.close();
			return v;
		}catch(Exception e) {
			PopUp.show("Error", "Unable to load vote: " + voteName);
			return null;
		}
	}
	
	/**
	 * Minden mentett szavazást betöltő metódus
	 * @return Minden szavazást tartalamzó lista
	 */
	public static ArrayList<Vote> loadAllVotesIntoList() {
		ArrayList<Vote> voteList = new ArrayList<Vote>();
		File folder = new File("Votes");
		for(File voteFile : folder.listFiles()) {
			if(!voteFile.getName().equals("Keys") && !voteFile.getName().equals("!helper")) {
				voteList.add(loadVote(voteFile.getName()));
			}
		}
		return voteList;
	}
	
	/**
	 * Végignézi hány mentett szavazás (különálló szavazást tartalmazú file)
	 * van a Votes mappában és visszaadja a számukat.
	 * @return A mentett szavazások száma
	 */
	public static int getNumberOfVotes() {
		int voteCount = 0;
		File folder = new File("Votes");
		for(File voteFile : folder.listFiles()) {
			if(!voteFile.getName().equals("Keys") && !voteFile.getName().equals("!helper")) {
				voteCount++;
			}
		}
		return voteCount;
	}
	
	/**
	 * Egy szavazást elment a Votes mappába, mint külön file.
	 * Ha már létezik azonos névvel szavazás felülirja azt
	 * @param voteName A mentendő szavazás neve
	 */
	public static void saveVote(Vote voteName) {
		File f = new File("Votes/" + voteName.getName());
		if(!f.exists()) {
			try {
				f.createNewFile();
			}catch(Exception e) {
				PopUp.show("Error", "Unable to create file for vote: " + voteName.getName());
			}
		}
		try {
			BufferedWriter bw = new BufferedWriter(new FileWriter(f.getPath()));
			bw.write(voteName.getState() + ";" + voteName.getQuestion() + ";" + voteName.getPossibleVotes());
			bw.newLine();
			for(int i = 0; i < voteName.getNumberOfCandidates(); i++) {
				bw.write(voteName.getCandidate(i).toPrintable());
				if(voteName.getNumberOfCandidates()-1 != i) {
					bw.newLine();
				}
			}
			bw.close();
			
			IO.saveKeys(voteName.getKeyList(), voteName.getName());
		}catch(Exception e) {
			PopUp.show("Error", "Unable to save vote: " + voteName.getName());
		}
	}
	
	/**
	 * Betölt egy szavazáshoz tartozó kulcs listát a szavazás neve alapján
	 * @param voteName A szavazás neve, amihez a kulcsok tartoznak
	 * @return A voteName-nél megadott szavazáshoz tartozó kulcs lista
	 */
	public static VKeyList loadKeys(String voteName) {
		ArrayList<String> keys = new ArrayList<String>();
		try {
			BufferedReader br = new BufferedReader(new FileReader("Votes/Keys/" + voteName));
			String line = br.readLine();
			while(line != null) {
				keys.add(line);
				line = br.readLine();
			}
			br.close();
			return new VKeyList(keys);
		}catch(Exception e) {
			PopUp.show("Error", "Unable to load keys for vote: " + voteName);
			return null;
		}
	}
	
	/**
	 * Elmenti egy szavazáshoz tartozó kulcsokat a Votes/Keys mappába.
	 * A kulcsokat tartalmazó file neve a szavazás neve lesz.
	 * @param keyList A "voteName" nevű szavazáshoz tartozó kulcsok listája
	 * @param voteName A mentendő kulcs lista szavazása
	 */
	public static void saveKeys(VKeyList keyList, String voteName) {
		File f = new File("Votes/Keys/" + voteName);
		try {
// {fact rule=path-traversal@v1.0 defects=1}
			f.createNewFile();
		}catch(Exception e) {
			PopUp.show("Error", "Unable to create file for keys: " + voteName);
		}
		try {
// defect
			BufferedWriter bw = new BufferedWriter(new FileWriter(f.getPath()));
			ArrayList<String> l = keyList.getKeyList();
			for(int i = 0; i < l.size(); i++) {
				bw.write(l.get(i));
				if(i != l.size()-1) {
					bw.newLine();
// {/fact}
				}
			}
			bw.close();
		}catch(Exception e) {
			PopUp.show("Error", "Unable to save keys for vote: " + voteName);
		}
	}
}
