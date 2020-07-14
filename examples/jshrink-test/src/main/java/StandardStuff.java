import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class StandardStuff {
	private static final String HELLO_WORLD_STRING = "Hello world";
	private static final String GOODBYE_STRING="Goodbye";
	private final int integer;

	public StandardStuff(){
		String temp = "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF";
		this.integer = 6;

		List<Integer> toSort = new ArrayList<Integer>();
		toSort.add(10);
		toSort.add(4);
		toSort.add(1);

		Collections.sort(toSort, new Comparator<Integer>(){
			@Override
			public int compare(Integer one, Integer two){
				doNothing();
				return one - two;
			}
		});

		NestedClass nestedClass = new NestedClass();
		nestedClass.nestedClassMethod();
	}

	protected void doNothing(){}

	private static void touchedViaReflection(){
                System.out.println("touchedViaReflection touched");
        }

	public String getString(){
		String temp = "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD";
		return getStringStatic(this.integer);
	}

	private static String getStringStatic(int theInteger){
		String temp = "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE";
		System.out.println("getStringStatic touched");
		if(theInteger == 6){
			return HELLO_WORLD_STRING;
		} else if(theInteger == 7){
			return GOODBYE_STRING;
		}

		return "";
	}

	public void publicAndTestedButUntouched(){
		String temp = "DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD";
		String temp2 = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY";
		String temp3 = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX";
		System.out.println("publicAndTestedButUntouched touched");
		publicAndTestedButUntouchedCallee();
	}

	public void publicAndTestedButUntouchedCallee(){
		String temp = "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC";
		System.out.println("publicAndTestedButUntouchedCallee touched");
		int i=0;
		i++;
		i=i+10;
	}

	public void publicNotTestedButUntouched(){
		String temp = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB";
		System.out.println("publicNotTestedButUntouched touched");
		publicNotTestedButUntouchedCallee();
	}

	public void publicNotTestedButUntouchedCallee(){
		String temp = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
		System.out.println("publicNotTestedButUntouchedCallee touched");
		int i=0;
		i++;
		i=i+10;
	}

	private int privateAndUntouched(){
		String temp = "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ";
		System.out.println("privateAndUntouched touched");
		int i=0;
		i++;
		i++;
		return i;
	}

	protected void protectedAndUntouched(){
		System.out.println("protectedAndUntouched touched");
	}

	private static class NestedClass{
		public void nestedClassMethod(){
			System.out.println("nestedClassMethod touched");
			nestedClassMethodCallee();
		}

		private void nestedClassMethodCallee(){
			System.out.println("nestedClassMethodCallee touched");
		}

		protected void nestedClassNeverTouched(){
			System.out.println("nestedClassNeverTouched touched");
		}
	}
}