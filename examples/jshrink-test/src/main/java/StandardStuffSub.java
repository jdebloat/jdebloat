import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class StandardStuffSub extends StandardStuff {

	public StandardStuffSub(){
		super();
		protectedAndUntouched();
	}

	@Override
	protected void protectedAndUntouched(){
		System.out.println("protected And Untouched (StandardStuffSub) touched");
	}

	protected void subMethodUntouched(){
		System.out.println("SubMethodUntouched touched");
	}

}