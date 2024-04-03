import { useEffect } from 'react'; // useEffect 임포트 추가
import Navbar from "../components/commonUseComponents/Navbar";
import Poket from "../components/commonUseComponents/Poket";
import Banner from "../components/mainComponents/Banner";
import Game from "../components/mainComponents/Game"
import Select from "../components/mainComponents/Select"
import useHotTopicStore from "../stores/hotTopicStore";
import useUserStore from "../stores/userStore";
function Main() {
  const { user } = useUserStore();
  // const { fetchNewsData, newsFetched, nLoading } = useHotTopicStore(); // 상태와 함수 추출
  const {  newsFetched, nLoading } = useHotTopicStore(); // 상태와 함수 추출
  
  //news
  useEffect(() => {
    // if (user && !newsFetched && !nLoading) {
    //   fetchNewsData();
    //   // .then() 호출 및 setNewsFetched(true)는 fetchNewsData 내부에서 처리
    // }
  }, [user, newsFetched, nLoading]); // setNewsFetched 제거
  
  
  return (
    
    <>
    <div className="flex">
    <Navbar /> {/* 네브바를 화면의 왼쪽에 고정 */}
    <Poket />
    <div className="pl-72 pr-36 w-full"> {/* 네브바 옆으로 메인 컨텐츠를 배치하되, pl-64를 사용하여 네브바의 너비만큼 패딩을 줍니다. */}
    <div className="max-w-full overflow-hidden"> {/* overflow-hidden을 사용하여 화면 너비를 초과하는 내용이 스크롤되지 않도록 합니다. */}
        <Banner />
        <Select />
        <Game />
    </div>
    </div>
    </div>
    </>
  );
}
export default Main;
