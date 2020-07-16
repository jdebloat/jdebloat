import org.junit.Test;

import java.io.IOException;

import static org.junit.Assert.assertEquals;
import java.io.IOException;

public class ApplicationTest {
  @Test public void squareTest() {
    for(int i = 0; i < 1_000_000; i++) {
      assertEquals(square(2), 4);
    }
  }

  private int square(int a) {
    Application app = new Application();
    return app.square(a);
  }
};
