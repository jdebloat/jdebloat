import edu.ucla.cs.onr.test.Library;

public class Application {
	public static void main(String[] args) {
    System.out.println(square(2));
		return;
	}

  public static int square(int num) {
    Library lib = new Library();
    return lib.square(num);
  }
};
